import pandas as pd
import numpy as np
from itertools import chain
import time
import msgpack
import multiprocessing as mp
import os
import ntpath
import ujson


from utils import submit_job
from config import *

# TODO wait for openpose to finish running, then run condensation code


def run_openpose(vid_path, op_output_dir, face=True, hand=True, overwrite=False, **kwargs):
    """run_openpose: submit sbatch job to run Openpose on given video.

    :param vid_path: path to video file.
    :param op_output_dir: directory that will house Openpose output folders.
    :param face: outputs face keypoints (in addition to pose keypoints) if True.
    :param hand: outputs hand keypoints (in addition to pose keypoints) if True.
    :param **kwargs: additional command-line arguments to pass to Openpose
    (see https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/demo_overview.md
    for complete documentation on command-line flags).

    Example usage:
    run_openpose('/path/to/myheadcamvid.mp4', '/path/to/output_dir',
                 keypoint_scale=3, frame_rotate=180)
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
    # print('command submitted to sbatch job: ', cmd)

    msg = submit_job(cmd, job_name=f'{vid_name}', p='gpu', t=5.0, mem='8G', gres='gpu:1')
    # print('command line output: ', msg)


def create_video_dataframe(vid_name, vid_json_files_dir, save_path=None):
    vid_df = pd.DataFrame()
    vid_df['openpose_npy'] = jsons_to_npy(vid_json_files_dir)
    vid_df['frame_num'] = [i for i in range(len(vid_df))]
    if save_path:
        vid_df.to_json(save_path, index=False)

    return vid_df


def jsons_to_npy(json_files_dir):
    json_filepaths = sorted(os.listdir(json_files_dir))
    json_list = load_json_list(json_filepaths)
    npy = json_list_to_npy(json_list)
    return npy


def load_json_chunk(chunk):
    return [ujson.load(open(f, 'r')) for f in chunk]


def load_json_list(json_filepaths, part_size=10000, num_chunks=16):
    num_frames = len(json_filepaths)
    chunks = lambda fps, chunk_size: [fps[i:i+chunk_size]
                                    for i in range(0, part_size, chunk_size)]
    json_list = []
    print('loading json files...')
    for i in range(0, num_frames, part_size):
        print(f'{i}/{num_frames}')
        fps_cut = json_filepaths[i:i+part_size]
        p = mp.Pool()
        chunk_size = len(fps_cut) // num_chunks
        chunk_list = chunks(fps_cut, chunk_size)
        json_list += p.map(load_json_chunk, chunk_list)
    json_list = [frame for chunk in json_list for frame in chunk]
    print('done loading json files.')
    return json_list


def json_list_to_npy(json_list):
    """json_list_to_npy: converts list of json (dictionaries)
    for each frame to one numpy array

    :param json_list: list of dictionaries corresponding to Openpose keypoints
    for each frame of the video

    :return: numpy array containing Openpose keypoints for each person in each frame.
    the shape is as follows:

    (num_frames, max_num_people, (x, y, conf) = 3, num_keypoints = 130)

    in other words, for each frame, for each person in that frame,
    we have their keypoints stored in 3 slices of length 130,
    one for each of (x, y, conf).

    for frames with less than max_num_people, the remaining people's slices are filled with
    np.NaN.
    """
    def frame_to_npy(frame, max_num_people):
        """frame_to_npy: converts a single frame to npy
        """

        arr = np.full((max_num_people, 3, OPENPOSE_NUM_KEYPTS), np.NaN)
        people = frame['people']
        if len(people) == 0:
            return arr
        for i in range(max_num_people):
            for j in range(3): #x, y, and confidence
                l = []
                for keypt in people[i]:
                    l.extend(people[i][keypt][j::3])
                arr[i, j, :] = l
        return arr
    max_num_people = max(len(frame['people']) for frame in json_list)
    flattened = np.array([frame_to_npy(frame_json, max_num_people)
                          for frame_json in json_list])
    return flattened


def extract_face_hand(frame_df):
    """extract_face_hand: Extracts face and hand presence from the saved Openpose video keypoints for the entire dataset.

    :param frame_df: Dataframe with a row for each frame of video in the dataset.
    :return: frame_df, with additional columns attached indicating detection of a face ('face_openpose'),
    detection of a hand ('hand_openpose'), average nose keypoint confidence ('nose_conf'), and
    average wrist keypoint confidence ('wrist_conf').
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
    """extract_face_hand_video: Extracts nose and wrist keypoints (corresponding to face
    and hand presence) for a given video's Openpose outputs.

    :param frame_df: Dataframe with a row for each frame of video in the video.
    :return: list of [nose avg confidence, wrist avg confidence] for each frame of video
    """
    print(frame_df.name)
    with open(os.path.join(OPENPOSE_CONDENSED_OUTPUT, '{}.msgpack'.format(frame_df.name)), 'rb') as infile:
        vid_keypts = msgpack.unpack(infile)
    p = multiprocessing.Pool()
    return p.map(extract_face_hand_frame, vid_keypts) #list of lists


def extract_face_hand_frame(frame_keypts):
    """extract_face_hand_frame: extracts nose and wrist keypoints from Openpose output for a single frame

    :param frame_keypts: Dictionary of keypoints for an individual frame (Openpose format)
    :return: Average nose and average wrist confidence for the frame as a list
    if working with data loaded in byte-format from msgpack files,
    person['face_keypoints'] => person[b'face_keypoints'] and
    frame_keypts['people'] => frame_keypts[b'people']
    """

    # Single nose keypoint confidence for each person.
    nose_keypts = [get_keypoint_conf(person['face_keypoints'], OPENPOSE_FACE_NOSE_KEYPT)
                   for person in frame_keypts['people']]

    #Both left and right wrists for each person, flattened into 1-D list [L, R, L, R, ....].
    wrist_keypts = list(chain.from_iterable((get_keypoint_conf(person['pose_keypoints'], OPENPOSE_POSE_RIGHT_WRIST_KEYPT),
                                             get_keypoint_conf(person['pose_keypoints'], OPENPOSE_POSE_LEFT_WRIST_KEYPT))
                                            for person in frame_keypts['people']))

    nose_avg = 0 if len(nose_keypts) == 0 else np.average(nose_keypts)
    wrist_avg = 0 if len(wrist_keypts) == 0 else np.average(wrist_keypts)

    return [nose_avg, wrist_avg]


def get_keypoint_conf(keypt_list, keypt_num):
    """get_keypoint_conf: extract the keypoint specified by keypt_num from Openpose keypoint list.

    :param keypt_list: list of Openpose keypoints in [x, y, conf, x, y, conf ...] format
    :param keypt_num: number of keypoint to extract for keypt_list.
    See https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md for description of keypoint maps.
    :return: confidence in range [0, 1]

    Example usage:
    get_keypoint_conf(face_keypoints, 30)
    """
    return keypt_list[keypt_num*3+2]
