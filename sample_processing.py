import os
import sys
sys.path.insert(0, "/scratch/users/agrawalk/headcam-algo/PCN/")

import matplotlib.pyplot as plt
import pandas as pd
import cv2
import numpy as np

from detector import FaceDetector


# converts int num to string, and adds zeros to get to length 5, if necessary.
def format_num(num):
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

# respond 'y' for face, 'n' or '' for no face, 'g' to go back and re-annotate prev frame
def get_annotation_input():
    annot = input('Face? (y/[n]/g[o back]) ').lower()
    while annot not in ['y', 'n', '', 'g']:
        annot = input('Invalid input.\nFace? (y/[n]/g[o back])').lower()
    print('Recorded \'{}\''.format(annot))
    return annot

#annotate frames in a given directory for faces (y/n); append annotations to dataframe
def annotate_sample(frames_dir, sample_json_path):
    df = pd.read_json(sample_json_path) # assumes a header is already present.
    img_paths = [os.path.join(frames_dir, '{0}_frames/image-{1}.jpg'.format(vid_name, format_num(num)))
                 for vid_name, num in zip(df['vid_name'], df['frame'])]
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
def calc_prf(df, det_name):
    pos = df[df['face_{}'.format(det_name)]]
    true = df[df['face_present'] == 1]
    true_pos = pos[pos['face_present'] == 1]

    p = len(true_pos) / len(pos)
    r = len(true_pos) / len(true)
    denom = 1 if p + r == 0 else p + r
    f1 = 2 * p * r / denom
    return p, r, f1
    # return len(pos), len(true), len(true_pos), round(p, 2), round(r, 2), round(f1, 2)

def display_prf(sample_json_path, det_names = ['vj', 'mtcnn', 'openpose']):
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

def display_prf2(sample_json_path, det_names = ['vj', 'mtcnn', 'openpose']):
    df = pd.read_json(sample_json_path)

    for vid_name in df['vid_name'].unique():
        vid_slice = df[df['vid_name'] == vid_name]
        print('VID: {0} ({1} frames)'.format(vid_name, len(vid_slice)))
        slices = {'face': vid_slice[vid_slice.index >= 1200], 'random': vid_slice[vid_slice.index < 1200]}
        for det_name in det_names:
            print('\tDETECTOR: {}'.format(det_name))
            for group in slices:
                group_slice = slices[group]
                npos, ntrue, ntrue_pos, p, r, f1 = calc_prf(group_slice, det_name)
                print('\t[{3}] precision: {0}, recall: {1}, F1: {2}\n'.format(p, r, f1, group))
            print()

#pads the number w/ zeros, as per openpose output JSON files
def openpose_format_num(num):
    num = str(num)
    return '0' * (12 - len(num)) + num

#apply function on each row, return row with openpose info for keypoint
def create_openpose_col(row, openpose_dir, keypoint):
    fname = '{0}_{1}_keypoints.json'.format(row['vid_name'],
                                            openpose_format_num(row['frame'] - 1))
    path = os.path.join(openpose_dir, '{}.AVI'.format(row['vid_name']), fname)
    op_df = pd.read_json(path)
    #returns list of keypoint-lists
    return [person[keypoint] for person in op_df['people'].values]

#add openpose columns to dataframe
def incorporate_openpose_output(sample_json, openpose_dir):
    df = pd.read_json(sample_json)
    for keypoint in ['pose_keypoints', 'face_keypoints', 'hand_left_keypoints', 'hand_right_keypoints']:
        df[keypoint] = df.apply(lambda row: create_openpose_col(row, openpose_dir, keypoint), axis=1)
    df.to_json(sample_json)
