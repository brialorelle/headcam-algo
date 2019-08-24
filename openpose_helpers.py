import time
import msgpack
import multiprocessing
import json
import os
import ntpath

from utils import submit_job
from config import *

#TODO: run_openpose() if condense() is true, the job that it submits also condenses once the openpose finishes.


def run_openpose(vid_path, op_output_dir, face=True, hand=False, overwrite=None, **kwargs):
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
        if (overwrite is None and input(f'overwrite existing directory {vid_output_dir}? (yes/no)') != 'yes') or not overwrite:
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

    msg = submit_job(cmd, job_name=f'{vid_name}', p='gpu', t=5.0, mem='8G', gres='gpu:1')
    print(msg)


def condense_openpose(frame_df):
    """condense_openpose: condenses folders of frame-level JSON outputs into video-level JSON
    outputs, stored as msgpack files.

    :param frame_df: df containing video name and frame for each frame.
    """
    portion_size = 2000000
    fps = []

    print('Collecting openpose filepaths....')

    for portion in range(0, len(frame_df), portion_size):
        data = zip(frame_df['vid_name'][portion:portion+portion_size].values,
                   frame_df['frame'][portion:portion+portion_size].values)
        p = multiprocessing.Pool()
        fps.extend(p.map(_openpose_filepath, data))

    print('Condensing into video-level files....')
    frame_df['op_file'] = fps
    g = frame_df.groupby('vid_name')


    g.apply(_save_vid_json)

def _openpose_filepath(tupl):
    """_openpose_filepath: applied function to generate openpose filepath.

    :param tupl: tuple of (vid_name, frame_num)
    """
    vid_name, frame_num = tupl
    vid_name = vid_name
    frame_num = str(frame_num).zfill(12)
    filename = f'{vid_name}_{frame_num}_keypoints.json'
    return os.path.join(OPENPOSE_OUTPUT, vid_name, filename)

def _save_vid_json(vid_df): #Returns a list of Openpose JSONs for that video
    """_save_vid_json: applied function to save a video df.

    :param vid_df: Pandas frame-level df for a given video.
    """
    vid_name = vid_df.name
    vid_df = vid_df.sort_values(by='frame')
    save_path = os.path.join(OPENPOSE_CONDENSED_OUTPUT, f'{vid_name}.msgpack')

    if os.path.exists(save_path):
        print(f'Already have {save_path}, continuing')
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

def create_openpose_columns(frame_df):
    #open video JSONs
    print('Opening video JSONs...')

    #Parse for wrist and nose


