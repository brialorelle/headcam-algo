import os
import re
import sys
import csv
import face
import ntpath
import traceback
import multiprocessing
from scipy import misc

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp/cpu_mtcnn_%s.csv")


def process_img(imgpath):
    img = misc.imread(imgpath)
    detector = face.Detection()

    faces = detector.find_faces(img)

    name = ntpath.basename(os.path.dirname(imgpath))
    group = str(int(name.split("_")[1][:2]))
    frame = re.search('image-(.*).jpg', ntpath.basename(imgpath)).group(1)

    rows = []

    if len(faces) == 0:
        rows.append([group, name, frame, False, None, None, None, None])
    else:
        for f in faces:
            arr = f.bounding_box
            x, y, w, h = arr[0], arr[1], arr[2], arr[3]
            rows.append([group, name, frame, True, x, y, w, h])

    return rows


if __name__ == "__main__":
    vid_folder = sys.argv[1]
    vid = ntpath.basename(vid_folder)

    pool = multiprocessing.Pool()
    results = []

    for image in os.listdir(vid_folder):
        results.append(pool.apply_async(process_img, args=(os.path.join(vid_folder, image),)))

    pool.close()

    with open(OUTPUT_FILE % vid, 'wb') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        # wr.writerow(['group', 'video', 'frame', 'is_face', 'x', 'y', 'w', 'h', 'angle'])

        for result in results:
            try:
                rows = result.get()
                for row in rows:
                    wr.writerow(row)
            except:
                traceback.print_exc()
