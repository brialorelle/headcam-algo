"""
Script to randomly sample 100 random frames
and save those frames to a folder.
"""
import ntpath
import os
import sys

import cv2
import pandas as pd


def save_frames(row):
    """ for each face-detected frame, saves the bounding box as an image """
    num = str(row['frame'])
    num = '0' * (5 - len(num)) + num
    img = cv2.imread(os.path.join(FRAME_DIR, 'image-{}.jpg'.format(num)))
    cv2.imwrite(os.path.join(OUT_DIR, 'image-{}.jpg'.format(num)), img)


if __name__ == '__main__':
    VID_FOLDER = sys.argv[1]
    if VID_FOLDER[-1] == '/':
        VID_FOLDER = VID_FOLDER[:-1]
    VID_NAME = ntpath.basename(VID_FOLDER).split('.')[0]
    FRAME_DIR = os.path.join(os.path.expandvars("$SCRATCH"),
                             'headcam-algo/tests/output/{}.AVI'.format(VID_NAME))
    OUT_DIR = os.path.join(os.path.expandvars("$SCRATCH"),
                           'headcam-algo/tests/output/{}_random2'.format(VID_NAME))
    CSV_DIR = os.path.join(os.path.expandvars("$SCRATCH"),
                           'headcam-algo/tests/output/{}_mtcnn.csv'.format(VID_NAME))

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    df = pd.read_csv(CSV_DIR)

    df.rename(columns={df.columns[0]: 'name',
                       df.columns[1]: 'frame',
                       df.columns[2]: 'face',
                       df.columns[3]: 'x1',
                       df.columns[4]: 'y1',
                       df.columns[5]: 'x2',
                       df.columns[6]: 'y2'}, inplace=True)

    df = df.sample(100)  # get random sample of df where 'face' is True
    df.apply(save_frames, axis=1)
