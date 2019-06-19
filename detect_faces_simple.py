"""
script for detecting faces, given a video frames folder and optionally a max frame length
"""
import csv
import multiprocess
import ntpath
import os
import traceback
import random
import re
import sys

import cv2
import pandas as pd
from mtcnn import face
from detector import FaceDetector


# detector = FaceDetector('mtcnn')

def process_img(imgpath, detector):
    img = cv2.imread(imgpath)

    # faces = detector.find_faces(img)
    faces = detector.detect_faces(img)

    vid_name = ntpath.basename(os.path.dirname(imgpath)).split('_')[0]
    # group = str(int(name.split("_")[1][:2]))
    # frame = -1
    frame = re.search('image-(.*).jpg', ntpath.basename(imgpath)).group(1)

    row = [vid_name, frame, len(faces) > 0, faces]

    return pd.DataFrame([row], columns=['vid_name', 'frame', 'face_mtcnn', 'bb_mtcnn'])

#TODO: figure out multiprocessing
def run_mtcnn_on_vid(frame_dir, out_json, max_frames):
    if frame_dir[-1] == '/':
        frame_dir = frame_dir[:-1]
    vid = ntpath.basename(frame_dir)

    # detector = face.Detection()
    detector = FaceDetector('mtcnn')
    # pool = multiprocess.Pool()
    results = []

    # currently samples <=10000 frames from the video
    for image in random.sample(os.listdir(frame_dir), min(len(os.listdir(frame_dir)), 10000)):
        results.append(process_img(os.path.join(frame_dir, image), detector))
        # results.append(pool.apply_async(process_img, args=(os.path.join(frame_dir, image),)))

    # pool.close()
    OUTPUT_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gold_set.json")
    if os.path.isfile(OUTPUT_FILE):
        sample_df = pd.read_json(OUTPUT_FILE)
    else:
        sample_df = pd.DataFrame(columns=['vid_name', 'frame', 'face_mtcnn', 'bb_mtcnn'])
    for result in results:
        sample_df = sample_df.append(result, ignore_index=True)
        # try:
            # result = result.get()
            # sample_df = sample_df.append(result, ignore_index=True)
        # except:
        #     traceback.print_exec()
    sample_df.to_json(OUTPUT_FILE)

if __name__ == "__main__":
    run_mtcnn_on_vid(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) >= 4 else 10000)
