"""
Script to randomly sample 500 frames with face detections,
and save those frames to a folder.
"""
import os

import pandas as pd

import cv2

HOME_DIR = '/scratch/users/agrawalk/'
FRAME_DIR = os.path.join(HOME_DIR, 'testvid')
OUT_DIR = os.path.join(HOME_DIR, 'headcam-algo/tests/output/face_frames')
CSV_DIR = os.path.join(HOME_DIR, 'headcam-algo/tests/cpu_mtcnn_test.csv')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

df = pd.read_csv(CSV_DIR, header=None)

df.rename(columns={df.columns[0]: 'name',
                   df.columns[1]: 'frame',
                   df.columns[2]: 'face',
                   df.columns[3]: 'x',
                   df.columns[4]: 'y',
                   df.columns[5]: 'w',
                   df.columns[6]: 'h'}, inplace=True)
df = df[df['face']].sample(500)  # get slice of dataframe with face detected
print(df.head())


def save_frames(row):
    """ for each face-detected frame, saves the bounding box as an image """
    x, y, w, h = int(row['x']), int(row['y']), int(row['w']), int(row['h'])
    num = '0' * (5 - len(str(row['frame']))) + str(row['frame'])
    img = cv2.imread(os.path.join(FRAME_DIR, 'image-{}.jpg'.format(num)))
    img = img[y:y+h, x:x+w]
    cv2.imwrite(os.path.join(OUT_DIR, 'crop_image-{}.jpg'.format(num)), img)


df.apply(save_frames, axis=1)
