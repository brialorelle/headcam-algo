import ujson as json
import pandas as pd
import numpy as np
from itertools import chain
import time
import msgpack
import multiprocessing
import json
import os
import ntpath

from utils import submit_job
from config import *

#TODO: run_openpose() if condense() is true, the job that it submits also condenses once the openpose finishes.


def run_openpose(vid_path, op_output_dir, face=True, hand=True, overwrite=False, **kwargs):
    """run_openpose: submit sbatch job to run Openpose on given video.

    :param vid_path: path to video file.
    :param op_output_dir: directory containing Openpose output folders.
    :param face: outputs face keypoints if True.
    :param hand: outputs hand keypoints if True.
    :param **kwargs: additional command-line arguments to pass to Openpose (see Openpose
    demo documentation).
    """
    os.makedirs(op_output_dir, exist_ok=True)
    vid_name = ntpath.basename(vid_path)[:-4]
    vid_output_dir = os.path.join(op_output_dir, f'{vid_name}')

    if os.path.exists(vid_output_dir):
        if not overwrite and input(f'overwrite existing directory {vid_output_dir}? (yes/no)') != 'yes':
            print(f'aborting on video {vid_path}.')
            return
    os.makedirs(vid_output_dir, exist_ok=True)

    #this could also be openpose_latest.sif, instead of openpose-latest.img.
    cmd = 'singularity exec --nv $SINGULARITY_CACHEDIR/openpose-latest.img bash -c \''
    cmd += 'cd /openpose-master && ./build/examples/openpose/openpose.bin '
    cmd += f'--video {vid_path} '
    for opt, optval in kwargs.items():
        cmd += f'--{opt} {optval} '
    if face:
        cmd += '--face '
    if hand:
        cmd += '--hand '
    cmd += f'--write_keypoint_json {vid_output_dir}\''
    print('command submitted to sbatch job: ', cmd)

    msg = submit_job(cmd, job_name=f'{vid_name}', p='gpu', t=5.0, mem='8G', gres='gpu:1')
    print('command line output: ', msg)


def collect_filepaths(frame_df, portion_size=2000000, verbose=False):
    """collect_filepaths: aggregates Openpose filepaths from given frame dataframe.

    :param frame_df: Pandas frame-level dataframe.
    :param portion_size: chunk size to pass to multiprocessing
    :param verbose: if True, prints progress.
    """
    fps = []
    for portion in range(0, len(frame_df), portion_size):
        if verbose:
            print(f'progress: {portion}/{len(frame_df)}')
        data = zip(frame_df['vid_name'][portion:portion+portion_size].values,
                   frame_df['frame'][portion:portion+portion_size].values)
        p = multiprocessing.Pool()
        fps.extend(p.map(_openpose_filepath, data))
    return fps

def condense_openpose(frame_df, fps=None, overwrite=False):
    """condense_openpose: condenses folders of frame-level JSON outputs into video-level JSON
    outputs, stored as msgpack files.

    :param frame_df: df containing video name and frame for each frame.
    :param fps: Openpose filepaths; if provided, skips filepath collection
    :param overwrite: if True, overwrites existing msgpack files.
    """

    if fps is None:
        print('Collecting openpose filepaths....')
        fps = collect_filepaths(frame_df)
        frame_df['op_file'] = fps
    else:
        print('Using provided filepaths. Skipping collection')

    print('Condensing into video-level files....')
    g = frame_df.groupby('vid_name')
    g.apply(lambda df: _save_vid_json(df, overwrite))

def _openpose_filepath(tupl):
    """_openpose_filepath: applied function to generate filepaths for raw Openpose outputs.

    :param tupl: tuple of (vid_name, frame_num)
    """
    vid_name, frame_num = tupl
    vid_name = vid_name
    frame_num = str(frame_num).zfill(12)
    filename = f'{vid_name}_{frame_num}_keypoints.json'
    return os.path.join(OPENPOSE_OUTPUT, vid_name, filename)

def _save_vid_json(vid_df, overwrite): #Returns a list of Openpose JSONs for that video
    """_save_vid_json: applied function to save a video df.

    :param vid_df: Pandas frame-level df for a given video.
    """
    vid_name = vid_df.name
    vid_df = vid_df.sort_values(by='frame')
    save_path = os.path.join(OPENPOSE_CONDENSED_OUTPUT, f'{vid_name}.msgpack')

    if os.path.exists(save_path):
        print(f'Overwriting save path {save_path} !' if overwrite else f'Already have {save_path}, continuing')
        if not overwrite:
            return


    print(f'vidname: {vid_name} len: {len(vid_df)}')
    start = time.time()
    p = multiprocessing.Pool()
    json_list = p.map(_get_json, vid_df['op_file'].values)
    print(f'vidname: {vid_name} took {time.time() - start} secs')
    with open(save_path, 'wb') as outfile:
        msgpack.pack(json_list, outfile)

def _get_json(fp):
    """_get_json: opens JSON file at given path.

    :param fp: Path to JSON file.
    """
    try:
        return json.load(open(fp, 'r'))
    except:
        print(f"Could not open {fp}")

def extract_face_hand(frame_df):
    """extract_face_hand: Extracts face and hand presence from the saved Openpose video keypoints for the entire dataset.

    :param frame_df: Dataframe with a row for each frame of video in the dataset.
    """
    print('Opening/extracting keypoints from video JSONs...')

    frame_df = frame_df.sort_values(by=['vid_name', 'frame'])

    vid_groups = frame_df.groupby('vid_name')
    nose_wrist_keypts = vid_groups.apply(extract_face_hand_video)
    nose_wrist_keypts = [item for sublist in nose_wrist_keypts for item in sublist] #flatten

    print('Attaching nose and wrist columns to dataframe...')
    frame_df['nose_conf'], frame_df['wrist_conf'] = zip(*nose_wrist_keypts)
    frame_df['face_openpose'] = frame_df['nose_conf'] > 0
    frame_df['hand_openpose'] = frame_df['wrist_conf'] > 0

    print('Downcasting columns...')
    frame_df['nose_conf'] = pd.to_numeric(frame_df['nose_conf'], downcast='float')
    frame_df['wrist_conf'] = pd.to_numeric(frame_df['wrist_conf'], downcast='float')

    return frame_df

def extract_face_hand_video(frame_df):
    """extract_face_hand_video: Extracts nose and wrist keypoints (corresponding to face and hand presence) for a given video's Openpose outputs.

    :param frame_df: Dataframe with a row for each frame of video in the video.
    """
    print(frame_df.name)
    with open(os.path.join(OPENPOSE_CONDENSED_OUTPUT, '{}.msgpack'.format(frame_df.name)), 'rb') as infile:
        vid_keypts = msgpack.unpack(infile)
    p = multiprocessing.Pool()
    return p.map(extract_face_hand_frame, vid_keypts) #list of lists

def extract_face_hand_frame(keypts):
    """extract_face_hand_frame: extracts nose and wrist keypoints from Openpose output for a single frame

    :param keypts: Dictionary of keypoints for an individual frame (Openpose format)
    """
    #Single nose keypoint for each person.
    nose_keypts = [person[b'face_keypoints'][92] for person in keypts[b'people']]

    #Both left and right wrists for each person, flattened into 1-D list [L, R, L, R, ....].
    wrist_keypts = list(chain.from_iterable((person[b'pose_keypoints'][4], person[b'pose_keypoints'][7]) for person in keypts[b'people']))

    nose_avg = 0 if len(nose_keypts) == 0 else np.average(nose_keypts)
    wrist_avg = 0 if len(wrist_keypts) == 0 else np.average(wrist_keypts)

    return [nose_avg, wrist_avg]

