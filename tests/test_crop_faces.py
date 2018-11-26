"""Script that takes in a CSV with face detection info, and extracts the frames
with face detections."""

import os

import cv2
import pandas as pd

HOME_DIR = '/scratch/users/agrawalk/'
FRAME_DIR = os.path.join(HOME_DIR, 'testvid')
OUT_DIR = os.path.join(HOME_DIR, 'testcrop')
CSV_DIR = os.path.join(HOME_DIR, 'cpu_mtcnn_test.csv')
df = pd.read_csv(CSV_DIR, header=None)
# print(df.head())

df.rename(columns={df.columns[0]: 'name',
                   df.columns[1]: 'frame',
                   df.columns[2]: 'face',
                   df.columns[3]: 'x',
                   df.columns[4]: 'y',
                   df.columns[5]: 'w',
                   df.columns[6]: 'h'}, inplace=True)
df = df[df['face'] is True]  # get slice of dataframe where face is detected


def save_cropped(row):  # for each face-detected frame, saves the bounding box
    # as an image
    x, y, w, h = int(row['x']), int(row['y']), int(row['w']), int(row['h'])
    num = '0' * (5 - len(str(row['frame']))) + str(row['frame'])
    img = cv2.imread(os.path.join(FRAME_DIR, 'image-{}.jpg'.format(num)))
    img = img[y:y+h, x:x+w]
    cv2.imwrite(os.path.join(OUT_DIR, 'crop_image-{}.jpg'.format(num)), img)


df.apply(save_cropped, axis=1)
