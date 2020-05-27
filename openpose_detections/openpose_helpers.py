import warnings
import multiprocessing as mp
import os
from itertools import chain
import time

import pandas as pd
import numpy as np
# import msgpack
import ntpath
import ujson

# from utils import submit_job
from config import *

def create_video_dataframe(vid_json_files_dir, save_path=None):
    vid_df = pd.DataFrame()
    vid_df['openpose_npy'] = list(jsons_to_npy(vid_json_files_dir))
    vid_df['frame_num'] = [i for i in range(len(vid_df))]
    if save_path:
        vid_df.to_json(save_path)
    return vid_df


def recover_npy(vid_df):
    # will be useful in classifier work, when we want the original numpy array back
    return np.stack(vid_df['openpose_npy'], axis=0).astype(np.float)


def jsons_to_npy(json_files_dir):
    # breakpoint()
    json_filepaths = sorted(os.path.abspath(os.path.join(json_files_dir, f))
                            for f in os.listdir(json_files_dir))
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
        for i in range(len(people)):
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

def extract_face_hand_presence(vid_df, face_keypt=NPY_FACE_START + OPENPOSE_FACE_NOSE_KEYPT,
                               hand_keypts=[NPY_POSE_START + OPENPOSE_POSE_LEFT_WRIST_KEYPT,
                                            NPY_POSE_START + OPENPOSE_POSE_RIGHT_WRIST_KEYPT]):
    """extract_face_hand: Extracts face and hand presence from the saved Openpose video keypoints for the entire dataset.

    :param vid_df: Dataframe containing openpose outputs in column 'openpose_npy' for a given video.
    :param face_keypt: the keypoint that we wish to use as a proxy for face presence
    :param hand_keypts: the list of keypoints that we wish to use as a proxy for hand presence

    (Pass in the keypoint as NPY_*_START + keypoint_num, where

    NPY_*_START is the starting index of the appropriate keypoint map (defined in config.py), and
    keypoint_num is the number of that keypoint as specified by
    https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md)

    :return: vid_df, with additional columns attached indicating detection of a face ('face_openpose'),
    and average nose keypoint confidence ('nose_conf')
    """
    openpose_npy = recover_npy(vid_df)

    # I expect to see RuntimeWarnings in this block
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # average over the num_people dimension, ignoring np.nan's (for nonexistent people)
        vid_df['nose_conf'] = np.nanmean(openpose_npy[:, :, 2, face_keypt], axis=1)
        vid_df['wrist_conf'] = np.nanmean(openpose_npy[:, :, 2, hand_keypts], axis=(1, 2))
    vid_df['face_openpose'] = vid_df['nose_conf'] > 0
    vid_df['hand_openpose'] = vid_df['wrist_conf'] > 0

    return vid_df
