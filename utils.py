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
# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2

# from detector import FaceDetector
from config import *


def submit_job(wrap_cmd, job_name='sbatch', mail_type='FAIL',
                  mail_user='agrawalk@stanford.edu', p='normal,hns', c=1, t=2, **kwargs):
    """submit_sbatch: Wrapper to submit sbatch jobs to Slurm.

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

def vid_info_dataframe(video_dirs):
    """vid_info_dataframe: creates a Pandas dataframe with information about each video in the
    dataset (name, child ID, Unix time, frame count, and FPS.)

    :param video_dirs: list of directories containing headcam videos to be analyzed.
    """
    vid_df = pd.DataFrame()
    vid_df['vid_path'] = list(chain.from_iterable(glob.glob(os.path.join(dir, '*')) for dir in video_dirs))
    info = vid_df.apply(lambda row: _get_vid_info(row['vid_path']), axis=1)
    vid_df[['vid_name', 'child_id', 'unix_time', 'frame_count', 'fps']] = info
    vid_df = vid_df.sort_values(by=['unix_time', 'vid_name']).reset_index(drop=True)

    return vid_df

def _get_vid_info(vid_path):
    """_get_vid_info: row-wise helper to vid_info_dataframe, returns the appropriate info for each
    row in the dataframe as a Series.

    :param vid_path: video file path.
    """
    def _get_vid_name(vid_path):
        return ntpath.basename(vid_path)[:-4]

    def _get_child_id(vid_name):
        child_id = re.search(r'([A-Z])_(?:\d+)_', vid_name).groups()[0]
        return child_id

    def _get_unix_time(vid_name):
        timestamp = re.search(r'(?:A|S|Y)_(\d+)_', vid_name).groups()[0]
        unix_time = time.mktime(datetime.datetime.strptime(timestamp, "%Y%m%d").timetuple())
        return unix_time

    def _get_frame_count_fps(vid_path):
        cap = cv2.VideoCapture(vid_path)
        frame_count, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS)
        return frame_count, fps

    vid_name = _get_vid_name(vid_path)
    return pd.Series([vid_name, _get_child_id(vid_name), _get_unix_time(vid_name), *_get_frame_count_fps(vid_path)])


def frame_info_dataframe(vid_level_df):
    """frame_info_dataframe: creates a pandas dataframe with a row for each frame of each video
    (providing a dataframe onto which to attach frame-level outputs from detectors later.)


    :param vid_level_df: Pandas dataframe containing each video, with name and frame count.
    """
    vid_names = []
    vid_paths = []
    child_ids = []
    frame_nums = []
    for i in range(len(vid_level_df)):
        video = vid_level_df.iloc[i]
        vid_names.extend([video['vid_name']]*video['frame_count'])
        vid_paths.extend([video['vid_path']]*video['frame_count'])
        child_ids.extend([video['child_id']]*video['frame_count'])
        frame_nums.extend([x for x in range(video['frame_count'])])

    frame_df = pd.DataFrame()
    frame_df['vid_name'] = vid_names
    frame_df['vid_path'] = vid_paths
    frame_df['child_id'] = child_ids
    frame_df['frame'] = frame_nums

    return frame_df


#NOTE: All stuff below here is old code. TODO: move to archival script, out of main repo.

#TODO: replace with zfill
def format_num(num):
    """format_num
    given an int num, converts to a string and pads with zeros, according to the file
    naming conventions for FFMPEG frame outputs.

    :param num: int representing the frame number
    """
    num = str(num)
    return '0' * (5 - len(num)) + num


#creates a sample dataframe with random samples from each video (100 random and 100 face).
def create_sample_json(master_json_path, sample_json_path, sample_size=100):
    """create_sample_json: Creates a sample dataframe from the dataframe found in master_json_path
    with samples from each video in the dataframe (sample_size random frames and sample_size face
    frames). For example, if frames from 6 videos are in the JSON and sample_size=200, creates a
    sample dataframe of size (200 + 200)*6 = 2400 frames.

    :param master_json_path: Path to the JSON containing all the frames for a video.
    :param sample_json_path: Path to the JSON containing sampled frames.
    :param sample_size: Number of frames to draw from both random and face-dense from each video
    """
    sample_df = pd.DataFrame(columns=['vid_name', 'frame', 'face_mtcnn', 'bb_mtcnn'])
    df = pd.read_json(master_json_path)
    dfs = [df[df['vid_name'] == vid] for vid in df['vid_name'].unique()]

    sample_df = sample_df.append([df.sample(sample_size) for df in dfs], ignore_index=True)
    sample_df = sample_df.append([df[df['face_mtcnn']].sample(sample_size) for df in dfs],
                                 ignore_index=True)

    if (os.path.exists(sample_json_path)
            and input(f'overwrite existing directory {sample_json_path}? (yes/no)') != 'yes'):
        print(f'aborting on creation of {sample_json_path}.')
        return

    sample_df.to_json(sample_json_path)

# respond 'y' for face, 'n' or '' for no face, 'g' to go back and re-annotate prev frame
def get_annotation_input():
    """get_annotation_input: Gets a yes/no input from the user.
    """
    annot = input('Face? (y/[n]/g[o back]) ').lower()
    while annot not in ['y', 'n', '', 'g']:
        annot = input('Invalid input.\nFace? (y/[n]/g[o back])').lower()
    print('Recorded \'{}\''.format(annot))
    return annot

#annotate frames in a given directory for faces (y/n); append annotations to dataframe
def annotate_sample(frames_dir, sample_json_path):
    """annotate_sample: Helper to quickly hand-annotate frames, displayed to the user, for presence
    of face (y/n).

    :param frames_dir: directory containing the extracted video frames.
    :param sample_json_path: path to the sample json
    """
    df = pd.read_json(sample_json_path) # assumes a header is already present.
    vid_path = lambda vid_name, num: os.path.join(frames_dir,
                                                  f'{vid_name}_frames/image-{format_num(num)}.jpg')
    img_paths = [vid_path(vid_name, num) for vid_name, num in zip(df['vid_name'], df['frame'])]
    imgs = [cv2.imread(path) for path in img_paths]
    face_present = np.zeros(df.shape[0])
    print('BEGIN ANNOTATING {}'.format(frames_dir))

    i = 0
    while i < len(imgs):
        if i % 100 == 0: #avoid catastrophes
            np.save('face_present.npy', face_present)
        print('\nImage {0}/{1}'.format(i + 1, len(imgs)))
        plt.imshow(imgs[i])
        plt.show()
        annot = get_annotation_input()
        if annot == 'g':
            print('Going back to previous frame')
            i -= 1
        else:
            face_present[i] = (annot == 'y')
            i += 1

    df['face_present'] = face_present
    print('Saving annotated df')
    df.to_json(sample_json_path)
    print('END ANNOTATING {}'.format(frames_dir))

#apply function on each row, return faces detected
def create_det_col(row, detector, frames_dir):
    """create_det_col: Runs the passed-in detector on the passed-in dataframe (row),
    applied across the dataframe to create a column of detections for that detector.
    :param row: row of a Pandas dataframe containing the video name and frame number
    :param detector: FaceDetector object to be run
    :param frames_dir: directory containing frames
    """
    fname = '{0}_frames/image-{1}.jpg'.format(row['vid_name'], format_num(row['frame']))
    img_path = os.path.join(frames_dir, fname)
    return detector.detect_faces(cv2.imread(img_path))

#run a detector on frames in sample
def run_detector_on_sample(det_name, frames_dir, sample_json_path):
    """run_detector_on_sample: runs the given detector on the frames in the sample JSON,
    saving the detections and corresponding bounding boxes as a new column in the dataframe.

    :param det_name: name of the detector to be used (e.g. 'mtcnn' or 'vj')
    :param frames_dir: directory containing frame directories.
    :param sample_json_path: path to the sample JSON.
    """
    df = pd.read_json(sample_json_path) # assumes a header is already present.
    detector = FaceDetector(det_name)
    df[f'bb_{det_name}'] = df.apply(lambda row: create_det_col(row, detector, frames_dir), axis=1)
    df[f'face_{det_name}'] = [len(faces) > 0 for faces in df['bb_{}'.format(det_name)]]
    df.to_json(sample_json_path)

#calculate/display precision, recall and F-score for each detector
#TODO: move visualization to function
def calc_tpr_fpr(df, det_name, threshold=0):
    """calc_tpr_fpr: given a dataframe and a detector, calculate True Positive and False Positive
    Rates.

    :param df: dataframe to perform calculations over.
    :param det_name: name of detector for which metrics will be calculated.
    :param threshold: confidence threshold for openpose
    """
    true = df[df['face_present'] == 1]
    false = df[df['face_present'] == 0]
    df = df[df['nose_confidence'] >= threshold]
    pos = df[df['face_{}'.format(det_name)]]
    true_pos = pos[pos['face_present'] == 1]
    false_pos = pos[pos['face_present'] == 0]

    tpr = len(true_pos) / max(1, len(true))
    fpr = len(false_pos) / max(1, len(false))
    return tpr, fpr

# return len(pos), len(true), len(true_pos), round(p, 2), round(r, 2), round(f1, 2)

def calc_prf_hand(df, det_name):
    """calc_prf: given a dataframe and a detector, calculate and return that detector's precision,
    recall, and F1 score.

    :param df: dataframe to perform calculations over.
    :param det_name: name of detector for which metrics will be calculated.
    """
    pos = df[df['hand_{}'.format(det_name)] == 1]
    true = df[df['hand_present'] == 1]
    true_pos = pos[pos['hand_present'] == 1]

    p = len(true_pos) / max(1, len(pos))
    r = len(true_pos) / max(1, len(true))
    denom = 1 if p + r == 0 else p + r
    f1 = 2 * p * r / denom
    return p, r, f1

# def calc_prf(df, det_name):
#     """calc_prf: given a dataframe and a detector, calculate and return that detector's precision,
#     recall, and F1 score.

#     :param df: dataframe to perform calculations over.
#     :param det_name: name of detector for which metrics will be calculated.
#     """
#     pos = df[df['face_{}'.format(det_name)] == 1]
#     true = df[df['face_present'] == 1]
#     true_pos = pos[pos['face_present'] == 1]

#     p = len(true_pos) / max(1, len(pos))
#     r = len(true_pos) / max(1, len(true))
#     denom = 1 if p + r == 0 else p + r
#     f1 = 2 * p * r / denom
#     return p, r, f1
# # return len(pos), len(true), len(true_pos), round(p, 2), round(r, 2), round(f1, 2)

def display_prf(sample_json_path, det_names=['vj', 'mtcnn', 'openpose']):
    """display_prf: Display the prf of the given dataframe, display the precision, recall, and F1
    score, split by first the detector, then the group (random or face,) then the video.

    :param sample_json_path: path to the JSON containing the dataframe.
    :param det_names: names of the detectors to display statistics for.
    """
    df = pd.read_json(sample_json_path)

    slices = {'face': df[df.index >= 1200], 'random': df[df.index < 1200]}
    for det_name in det_names:
        print('DETECTOR: {}'.format(det_name))
        for group in slices:
            group_slice = slices[group]
            print('\tGROUP: {0} ({1} frames)'.format(group, len(group_slice)))
            npos, ntrue, ntrue_pos, p, r, f1 = calc_prf(group_slice, det_name)
            # print('\tpositive: {0}, true: {1}, true positive: {2}'.format(npos, ntrue, ntrue_pos))
            print('\tprecision: {0}, recall: {1}, F1: {2}\n'.format(p, r, f1))

            for vid_name in df['vid_name'].unique():
                vid_slice = group_slice[group_slice['vid_name'] == vid_name]
                print('\tVID: {0} ({1} frames)'.format(vid_name, len(vid_slice)))
                npos, ntrue, ntrue_pos, p, r, f1 = calc_prf(vid_slice, det_name)
                # print('\tpositive: {0}, true: {1}, true positive: {2}'.format(npos, ntrue, ntrue_pos))
                print('\tprecision: {0}, recall: {1}, F1: {2}\n'.format(p, r, f1))

def display_prf2(sample_json_path, det_names=['vj', 'mtcnn', 'openpose']):
    """display_prf2: Display the prf of the given dataframe, display the precision, recall, and F1
    score, split by first the video, then the detector, then the group (random or face.)

    :param sample_json_path: path to the JSON containing the dataframe.
    :param det_names: names of the detectors to display statistics for.
    """
    df = pd.read_json(sample_json_path)

    for vid_name in df['vid_name'].unique():
        vid_slice = df[df['vid_name'] == vid_name]
        print('VID: {0} ({1} frames)'.format(vid_name, len(vid_slice)))
        slices = {'face': vid_slice[vid_slice.index >= 1200],
                  'random': vid_slice[vid_slice.index < 1200]}
        for det_name in det_names:
            print('\tDETECTOR: {}'.format(det_name))
            for group in slices:
                group_slice = slices[group]
                npos, ntrue, ntrue_pos, p, r, f1 = calc_prf(group_slice, det_name)
                print('\t[{3}] precision: {0}, recall: {1}, F1: {2}\n'.format(p, r, f1, group))
            print()

def print_prf(df):
    avg_metrics = defaultdict(lambda: defaultdict(list))
    vid_metrics = defaultdict(lambda: defaultdict(list))
    metrics = ['p', 'r', 'f']
    det_names = ['openpose']
    # det_names = ['mtcnn', 'vj', 'openpose']

    #Get metrics for each detector
    for random_group in [True, False]:
        for det in det_names:
            cut = df[df['random'] == random_group]

            #this is p/r/f for a given det/group
            prf = calc_prf(cut, det)

            #each element is p/r/f for a given det/group/vid
            prf_vids = [calc_prf(cut[cut['vid_name'] == vid_name], det) for vid_name in VID_NAMES]

            for i, metric in enumerate(metrics):
                avg_metrics[metric][det].append(prf[i])
                vid_metrics[metric][det].append([x[i] for x in prf_vids])
    # fig, ax = plt.subplots()
    index = np.arange(2)
    bar_width = 0.15
    opacity = 0.8

    colors = [f'C{n}' for n in range(10)]

    for j, metric in enumerate(metrics):
        metric_print = {'p': 'Precision', 'r': 'Recall', 'f': 'F-score'}
        print(metric_print[metric])

        #Bar chart plotting
        for i, det in enumerate(det_names):
            x = index + i*bar_width
            print(f'{det}: {avg_metrics[metric][det]}')
            # plt.bar(x, avg_metrics[metric][det], bar_width,
            #         alpha=opacity,
            #         color=colors[i],
            #         label=det)

        ##Line chart plotting
        #for i in range(len(VID_NAMES)):
        #    for k in range(2): #splitting by face/random
        #        #plot the scores for a given a metric, group, and video across detectors.
        #        metric_y = [vid_metrics[metric][det][k][i] for det in vid_metrics[metric]]
        #        metric_x = [index + i*bar_width for i in range(len(det_names))]
        #        plt.plot(metric_x, metric_y, color='C4', marker='o')

        # plt.xlabel('Group')
        # plt.ylabel('Scores')

        # plt.title(metric_print[metric])

        # plt.xticks(index + bar_width, ('random', 'face'))
        # plt.legend()

    # plt.show()

#pads the number w/ zeros, as per openpose output JSON files
def viz_prf(df):
    avg_metrics = defaultdict(lambda: defaultdict(list))
    vid_metrics = defaultdict(lambda: defaultdict(list))
    metrics = ['p', 'r', 'f']
    det_names = ['mtcnn', 'vj', 'openpose']

    #Get metrics for each detector
    for random_group in [True, False]:
        for det in det_names:
            cut = df[df['random'] == random_group]

            #this is p/r/f for a given det/group
            prf = calc_prf(cut, det)

            #each element is p/r/f for a given det/group/vid
            prf_vids = [calc_prf(cut[cut['vid_name'] == vid_name], det) for vid_name in VID_NAMES]

            for i, metric in enumerate(metrics):
                avg_metrics[metric][det].append(prf[i])
                vid_metrics[metric][det].append([x[i] for x in prf_vids])
    fig, ax = plt.subplots()
    index = np.arange(2)
    bar_width = 0.15
    opacity = 0.8

    colors = [f'C{n}' for n in range(10)]

    for j, metric in enumerate(metrics):
        plt.figure(j)

        #Bar chart plotting
        for i, det in enumerate(det_names):
            x = index + i*bar_width
            plt.bar(x, avg_metrics[metric][det], bar_width,
                    alpha=opacity,
                    color=colors[i],
                    label=det)

        #Line chart plotting
        for i in range(len(VID_NAMES)):
            for k in range(2): #splitting by face/random
                #plot the scores for a given a metric, group, and video across detectors.
                metric_y = [vid_metrics[metric][det][k][i] for det in vid_metrics[metric]]
                metric_x = [index + i*bar_width for i in range(len(det_names))]
                plt.plot(metric_x, metric_y, color='C4', marker='o')

        plt.xlabel('Group')
        plt.ylabel('Scores')

        metric_print = {'p': 'Precision', 'r': 'Recall', 'f': 'F-score'}
        plt.title(metric_print[metric])

        plt.xticks(index + bar_width, ('random', 'face'))
        plt.legend()

    plt.show()

#pads the number w/ zeros, as per openpose output JSON files
def openpose_format_num(num):
    """openpose_format_num: format a frame number as per the Openpose JSON output files

    :param num: the frame number (int.)
    """
    num = str(num)
    return '0' * (12 - len(num)) + num

#apply function on each row, return row with openpose info for keypoint
def create_openpose_col(row, openpose_dir, keypoint):
    """create_openpose_col: row-wise applied function to create a column containing openpose
    keypoints for the given keypoint type.

    :param row: Pandas dataframe row.
    :param openpose_dir: Directory containing Openpose output folders.
    :param keypoint: One of 'pose_keypoints', 'face_keypoints',
                     'hand_left_keypoints', 'hand_right_keypoints'
    """
    try:
        fname = '{0}_{1}_keypoints.json'.format(row['vid_name'],
                                                openpose_format_num(row['frame'] - 1))
        path = os.path.join(openpose_dir, '{}'.format(row['vid_name']), fname)
        op_df = pd.read_json(path)
        #returns list of keypoint-lists
        return [person[keypoint] for person in op_df['people'].values]
    except ValueError:
        print("encountered value error")
        return []

def create_face_openpose_col(row):
    """create_face_openpose_col: row-wise applied function to create a column with boolean
    True/False values, describing whether a face was detected or not. A face is said to be detected
    by Openpose if any non-zero face-keypoints are present in the Openpose detections.

    :param row: Pandas dataframe row.
    """
    return reduce(lambda x, y: x or y, [np.sum(face) != 0 for face in row['face_keypoints']], False)

def incorporate_openpose_output(sample_json, openpose_dir):
    """incorporate_openpose_output: incorporate openpose outputs into pandas dataframe as separate
    columns for each type of keypoint (face, pose, left hand, and right hand), and resave the
    dataframe.

    :param sample_json: Sample JSON to add Openpose info to.
    :param openpose_dir: Directory containing Openpose output folders.
    """
    df = pd.read_json(sample_json) if os.path.isfile(sample_json) else pd.DataFrame()
    for keypoint in ['pose_keypoints', 'face_keypoints',
                     'hand_left_keypoints', 'hand_right_keypoints']:
        df[keypoint] = df.apply(lambda r: create_openpose_col(r, openpose_dir, keypoint), axis=1)
    df['face_openpose'] = df.apply(create_face_openpose_col, axis=1)
    df.to_json(sample_json)

    return df


#TODO: move default parameters to config
#wrapper to submit an sbatch job on sherlock.
#TODO: write Openpose submission helper.

def visualize_detections(sample_json, det_names, sample_size=25, face=True):
    """visualize_detections: sample a few frames, and overlay the detections of the various
    detectors (if any) on that frame.

    :param sample_json: path to the sample JSON.
    :param det_names: list of names of the detectors to be visualized (e.g. ['mtcnn', 'op', 'vj'])
    :param sample_size:
    :param face:
    """
    df = pd.read_json(sample_json)
    sample = df.sample(sample_size)

    #TODO: make load_frame(vid_name, frame) helper used here and in hand-annotation function

    # load images
    # create plot of 5*sample_size + (5 - sample size % 5) % 5
