import swifter
import msgpack
import ujson
import imutils
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import chain
import glob
import time
import datetime
import re
import ntpath
import os
import sys
import subprocess
from functools import reduce
from collections import defaultdict
import pandas as pd
import numpy as np
import cv2

from config import *


def submit_job(wrap_cmd, job_name='sbatch', mail_type='FAIL',
                  mail_user='agrawalk@stanford.edu', p='normal,hns', c=1, t=2, **kwargs):
    """submit_job: Wrapper to submit sbatch jobs to Slurm.

    :param wrap_cmd: command to execute in the job.
    :param job_name: name for the job.
    :param mail_type: mail upon success or fail.
    :param mail_user: user email.
    :param p: partitions to select from.
    :param c: Number of cores to use.
    :param t: Time to run the job for.
    :param **kwargs: Additional command-line arguments to sbatch. See Slurm/sherlock docs.
    """
    args = []
    args.extend(['-p', str(p)])
    args.extend(['-c', str(c)])
    args.extend(['-t', _job_time(t)])
    args.extend(['--job-name', job_name])
    args.extend(['--mail-type', mail_type])
    args.extend(['--mail-user', mail_user])

    for opt, optval in kwargs.items():
        args.extend(['--' + opt, optval])
    args.extend(['--wrap', wrap_cmd])

    p = subprocess.Popen(['sbatch'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

def _job_time(t):
    """_job_time: Converts time t to slurm time ('hh:mm:ss').

    :param t: a float representing # of hours for the job.
    """
    hrs = int(t//1)
    mins = int(t*60%60)
    secs = int(t*3600%60)

    return f'{str(hrs).zfill(2)}:{str(mins).zfill(2)}:{str(secs).zfill(2)}'

def vid_info_dataframe(video_dirs, birthdates, save_path=None):
    """vid_info_dataframe: creates a Pandas dataframe with information about each video in the
    dataset (name, child ID, Unix time, frame count, and FPS.)

    :param video_dirs: list of directories containing headcam videos to be analyzed.
    :param birthdates: dictionary from child id:birthdate as (YYYY, MM, DD.)
    :param save_path: JSON filepath to save dataframe at.
    """
    if save_path is not None and os.path.exists(save_path):
        print(f'Vid info dataframe at {save_path} already exists...loading old dataframe.')
        vid_df = pd.read_json(save_path)
        return vid_df

    print(f'Generating video dataframe from {video_dirs}...')
    vid_df = pd.DataFrame()
    vid_df['vid_path'] = list(chain.from_iterable(glob.glob(os.path.join(dir, '*')) for dir in video_dirs))
    info = vid_df.swifter.apply(lambda row: _get_vid_info(row['vid_path'], birthdates), axis=1)
    vid_df[['vid_name', 'child_id', 'unix_time', 'age_days', 'frame_count', 'fps']] = info
    vid_df = vid_df.sort_values(by=['vid_name']).reset_index(drop=True)

    if save_path is not None:
        print('Saving video dataframe...')
        vid_df.to_json(save_path)

    return vid_df

def _get_vid_info(vid_path, birthdates):
    """_get_vid_info: row-wise helper to vid_info_dataframe, returns the appropriate info for each
    row in the dataframe as a Series.

    :param vid_path: video file path.
    :param birthdates: dictionary from child id:birthdate as (YYYY, MM, DD.)
    """
    def _get_vid_name(vid_path):
        return ntpath.basename(vid_path)[:-4]

    def _get_child_id(vid_name):
        child_id = re.search(r'([A-Z])_(?:\d+)_', vid_name).groups()[0]
        return child_id

    def _get_unix_time_age_days(vid_name, birthdates):
        tupl = re.search(r'(A|S|Y)_(\d+)_', vid_name).groups()
        child_id, timestamp = tupl[0], tupl[1]
        unix_time = datetime.datetime.strptime(timestamp, "%Y%m%d")
        year, month, day = birthdates[child_id]
        age_days = (unix_time - datetime.datetime(year, month, day)).days
        return unix_time, age_days

    def _get_frame_count_fps(vid_path):
        cap = cv2.VideoCapture(vid_path)
        frame_count, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS)
        return frame_count, fps

    vid_name = _get_vid_name(vid_path)
    return pd.Series([vid_name, _get_child_id(vid_name), *_get_unix_time_age_days(vid_name, birthdates), *_get_frame_count_fps(vid_path)])


def frame_info_dataframe(vid_df, save_path=None):
    """frame_info_dataframe: creates a pandas dataframe with a row for each frame of each video
    (providing a dataframe onto which to attach frame-level outputs from detectors later.)

    :param vid_df: Pandas dataframe containing each video, with name and frame count.
    :param save_path: HDF5 filepath to save frame dataframe to.
    """
    if save_path is not None and os.path.exists(save_path):
        print(f'Frame info dataframe at {save_path} already exists...loading old dataframe.')
        frame_df = pd.read_hdf(save_path, key='master_frames')
        return frame_df

    vid_names = []
    vid_paths = []
    child_ids = []
    frame_nums = []
    unix_times = []
    age_days = []

    print('Creating columns...')
    for i in range(len(vid_df)):
        video = vid_df.iloc[i]
        vid_names.extend([video['vid_name']]*video['frame_count'])
        vid_paths.extend([video['vid_path']]*video['frame_count'])
        child_ids.extend([video['child_id']]*video['frame_count'])
        frame_nums.extend([x for x in range(video['frame_count'])])
        unix_times.extend([(video['unix_time'])]*video['frame_count'])
        age_days.extend([(video['age_days'])]*video['frame_count'])

    print('Attaching columns to dataframe...')
    frame_df = pd.DataFrame()
    frame_df['vid_name'] = vid_names
    frame_df['vid_path'] = vid_paths
    frame_df['child_id'] = child_ids
    frame_df['frame'] = frame_nums
    frame_df['unix_time'] = unix_times
    frame_df['age_days'] = age_days

    print('Sorting dataframe...')
    frame_df = frame_df.sort_values(by=['vid_name', 'frame'])

    print('Downcasting columns...')
    frame_df['frame'] = pd.to_numeric(frame_df['frame'], downcast='unsigned')
    frame_df['age_days'] = pd.to_numeric(frame_df['age_days'], downcast='unsigned')
    for col in ['vid_name', 'vid_path', 'child_id', 'unix_time']:
        frame_df[col] = frame_df[col].astype('category')

    if save_path is not None:
        print('Saving dataframe as hdf5 store...')
        frame_df.to_hdf(save_path, 'master_frames', format='table')

    return frame_df

def save_object(fp, obj):
    """save_object: writes msgpack object to given filepath.

    :param fp: File path to which to write msgpack file.
    :param obj: object to save.
    """
    with open(fp, 'wb') as outfile:
        msgpack.pack(obj, outfile)

def load_object(fp):
    """load_object: loads and returns msgpack object at given filepath.

    :param fp: File path from which to read msgpack file.
    """
    with open(fp, 'rb') as infile:
        return msgpack.unpack(infile)

def viz_openpose(df, overlay_openpose=True, face_present=None, face_openpose=None, fig_save_path=None):
    """viz_openpose: vizualize openpose keypoints+confidences on a sample of frames from the
    supplied dataframe.

    :param df: Dataframe containing vid_path and frame number for each frame.
    :param overlay_openpose: if True, displays openpose keypoints. (NOTE: Takes longer)
    :param face_present: only select rows with face present.
    :param face_openpose: only select rows with face detected.
    :param fig_save_path: path, if provided, to save the displayed figure to.
    """

    if face_present is not None:
        df = df[df['face_present'] == face_present]
    if face_openpose is not None:
        df = df[df['face_openpose'] == face_openpose]
    sample = df.sample(min(25, len(df)))
    sample = sample.reset_index()
    f, axs = plt.subplots(5,5,figsize=(16,12))
    sample.apply(lambda row: viz_single_frame(row['vid_path'], row['frame'], get_img(row), axs[row.name // len(axs), row.name % (len(axs))], overlay_openpose=overlay_openpose), axis=1)
    if fig_save_path is not None:
        plt.savefig(fig_save_path)
    plt.show()

def get_op_xyconf(keypt_lists):
    x = []
    y = []
    conf = []
    for keypt in keypt_lists:
        x.append(keypt[0::3])
        y.append(keypt[1::3])
        conf.append(keypt[2::3])
    if x == [] or y == [] or conf == []:
        return [], [], []

    return x, y, conf

def get_pose_keypoints(vid_path, frame):
    vid_name = ntpath.basename(vid_path)[:-4]
    frame_num = str(frame).zfill(12)
    filename = f'{vid_name}.msgpack'
    fp = os.path.join(OPENPOSE_CONDENSED_OUTPUT, filename)
    if not os.path.exists(fp):
        print('uh-oh')
        return []
    with open(fp, 'rb') as infile:
        keypts = msgpack.unpack(infile)[frame]
    # print(keypts)
    return [person[b'pose_keypoints'] for person in keypts[b'people']]

def viz_single_frame(vid_path, frame, img, ax, bbs=[], overlay_openpose=False):

    for x, y, w, h in bbs:
        rect = patches.Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none')
        ax.add_patch(rect)

    if overlay_openpose:
        x_pose, y_pose, conf_pose = get_op_xyconf(get_pose_keypoints(vid_path, frame))
        x_face, y_face, conf_face = get_op_xyconf(get_face_keypoints(vid_path, frame))
        ax.scatter(np.array(x_pose)*img.shape[1], np.array(y_pose)*img.shape[0],
                   c=conf_pose if len(conf_pose) > 0 else None, cmap='viridis', s=8)

        ax.scatter(np.array(x_face)*img.shape[1], np.array(y_face)*img.shape[0],
                   c=conf_face if len(conf_face) > 0 else None, cmap='inferno', s=8)

    ax.imshow(img)

def get_face_keypoints(vid_path, frame):
    vid_name = ntpath.basename(vid_path)[:-4]
    frame_num = str(frame).zfill(12)
    filename = f'{vid_name}.msgpack'
    fp = os.path.join(OPENPOSE_CONDENSED_OUTPUT, filename)
    if not os.path.exists(fp):
        print('uh-oh')
        return []
    with open(fp, 'rb') as infile:
        keypts = msgpack.unpack(infile)[frame]
    # print(keypts)
    return [person[b'face_keypoints'] for person in keypts[b'people']]

def get_img(row):
    cap = cv2.VideoCapture(row['vid_path'])
    cap.set(cv2.CAP_PROP_POS_FRAMES, row['frame'])
    return imutils.rotate(cap.read()[1], VID_ROTATE)
