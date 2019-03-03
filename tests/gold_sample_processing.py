import pandas as pd
import cv2
import os
import numpy as np
from detector import FaceDetector

def format_num(num):
    """converts int num to string, and adds zeros to get to length 5, if necessary."""
    num = str(num)
    return '0' * (5 - len(num)) + num

#creates a sample dataframe with random samples from each video (100 random and 100 face).
def create_sample_json(master_json_path, sample_json_path, sample_size=100):
    sample_df = pd.DataFrame(columns=['vid_name', 'frame', 'face_mtcnn', 'bb_mtcnn'])
    df = pd.read_json(master_json_path)
    dfs = [df[df['vid_name'] == vid] for vid in df['vid_name'].unique()]

    sample_df = sample_df.append([df.sample(sample_size) for df in dfs], ignore_index=True)
    sample_df = sample_df.append([df[df['face_mtcnn']].sample(sample_size) for df in dfs], ignore_index=True)

    sample_df.to_json(sample_json_path)


#apply function on each row, return faces detected
def create_det_col(row, detector, frames_dir):
    fname = '{0}_frames/image-{1}.jpg'.format(row['vid_name'], format_num(row['frame']))
    img_path = os.path.join(frames_dir, fname)
    return detector.detect_faces(cv2.imread(img_path))

#run a detector on frames in sample
def run_detector_on_sample(detector_name, frames_dir, sample_json_path):
    df = pd.read_json(sample_json_path) # assumes a header is already present.
    detector = FaceDetector(detector_name)
    df['bb_{}'.format(detector_name)] = df.apply(lambda row: create_det_col(row, detector, frames_dir), axis=1)
    df['face_{}'.format(detector_name)] = [len(faces) > 0 for faces in df['bb_{}'.format(detector_name)]]
    df.to_json(sample_json_path)

#calculate/display precision, recall and F-score for each detector
#TODO: visualization
def display_prf(sample_json_path, det_names = ['vj', 'mtcnn']):
    df = pd.read_json(sample_json_path)
    true = df[df['face_present']]

    for det_name in det_names:
        pos = df[df['face_{}'.format(det_name)]]
        true_pos = pos[pos['face_present']]

        p = len(true_pos) / len(pos)
        r = len(true_pos) / len(true)
        f1 = 2 * p * r / (p + r)

        print('DETECTOR: {}'.format(det_name))
        print('positive: {0}, true: {1}, true positive: {2}'.format(len(pos), len(true), len(true_pos)))
        print('precision: {0}, recall: {1}, F1: {2}\n'.format(p, r, f1))

#pads the number w/ zeros, as per openpose output
def openpose_format_num(num):
    num = str(num)
    return '0' * (12 - len(num)) + num

#apply function on each row, return row with openpose info for keypoint
def create_openpose_col(row, openpose_dir, keypoint):
    fname = '{0}_{1}_keypoints.json'.format(row['vid_name'],
                                            openpose_format_num(row['frame'] - 1))
    path = os.path.join(openpose_dir, '{}.AVI'.format(row['vid_name']), fname)
    op_df = pd.read_json(path)
    #list of keypoint-lists
    return [person[keypoint] for person in op_df['people'].values]

#add openpose columns to dataframe
def incorporate_openpose_output(sample_json, openpose_dir):
    df = pd.read_json(sample_json)
    for keypoint in ['pose_keypoints', 'face_keypoints', 'hand_left_keypoints', 'hand_right_keypoints']:
        df[keypoint] = df.apply(lambda row: create_openpose_col(row, openpose_dir, keypoint), axis=1)
    df.to_json(sample_json)
