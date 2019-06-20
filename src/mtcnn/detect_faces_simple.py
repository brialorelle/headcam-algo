"""
script for detecting faces given a video frames folder
NOTE: this script does not use multiprocessing.
"""
import csv
# import multiprocessing
import ntpath
import os
# import traceback
import random
import re
import sys

import cv2
import face

# OUTPUT_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp/cpu_mtcnn_%s.csv")


def process_img(imgpath, detector):
    img = cv2.imread(imgpath)

    faces = detector.find_faces(img)

    name = ntpath.basename(os.path.dirname(imgpath))
    # group = str(int(name.split("_")[1][:2]))
    frame = re.search('image-(.*).jpg', ntpath.basename(imgpath)).group(1)

    rows = []

    if len(faces) == 0:
        rows.append([name, frame, False, None, None, None, None])
    else:
        for f in faces:
            arr = f.bounding_box
            x, y, x2, y2 = arr[0], arr[1], arr[2], arr[3]
            rows.append([name, frame, True, x, y, x2, y2])

    return rows


if __name__ == "__main__":
    vid_folder = sys.argv[1]
    vid = ntpath.basename(vid_folder[:-1])
    out_dir = os.path.join(os.path.expandvars("$SCRATCH"), 'headcam-algo/tests/output')

    # this is the output CSV with face detections for a given video.
    OUTPUT_FILE = os.path.join(out_dir, '{}_mtcnn.csv'.format(vid.split('.')[0]))

    detector = face.Detection()
    # pool = multiprocessing.Pool()
    results = []

    # currently samples 5000 frames from the video
    for image in random.sample(os.listdir(vid_folder), min(len(os.listdir(vid_folder)), 5000)):
        results.append(process_img(os.path.join(vid_folder, image), detector))
        # results.append(pool.apply_async(process_img, args=(os.path.join(vid_folder, image),)))

    # pool.close()
    with open(OUTPUT_FILE, 'wb') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['name', 'frame', 'face_detected', 'x1', 'y1', 'x2', 'y2'])
        for result in results:
            for row in result:
                wr.writerow(row)
