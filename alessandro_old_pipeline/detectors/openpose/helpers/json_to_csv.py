import os
import csv
import sys
import json
import ntpath

CSV_OUTPUT_DIR = os.path.expandvars("$HOME/xs-face/scripts/openpose/tmp")

<<<<<<< HEAD
=======
# TODO 1 index
# TODO 1229 is weird because title contains "cropped"
# TODO if no face or hand or whatever, fill in with 0s!!! first check if, and if not, extend with 0s

>>>>>>> 9a4186c0e9d6512bfab90963cec0765de442f88a
if __name__ == "__main__":
    video_full_path = sys.argv[1]
    video_filename = ntpath.basename(video_full_path)
    print(video_filename)

    subject = "_".join(video_filename.split("_")[:2])
    group = str(int(subject.split("_")[1][:2]))

    with open(os.path.join(CSV_OUTPUT_DIR, subject + ".csv"), "wb") as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)

        for filename in os.listdir(video_full_path):
            if "XS_1229" in filename:
                frame = filename.split("_")[4][7:]
            else:
                frame = filename.split("_")[3][7:]

            with open(os.path.join(video_full_path, filename), "rb") as json_file:
                data = json.load(json_file)
                people = data["people"]

            if people:
                for person in people:
                    row = [group, subject, frame]

                    if person["pose_keypoints"]:
                        row +=  person["pose_keypoints"]
                    else:
                        row += [0 for _ in xrange(18*3)]

                    if person["face_keypoints"]:
                        row += person["face_keypoints"]
                    else:
                        row += [0 for _ in xrange(70*3)]

                    if person["hand_left_keypoints"]:
                        row += person["hand_left_keypoints"]
                    else:
                        row += [0 for _ in xrange(21*3)]

                    if person["hand_right_keypoints"]:
                        row += person["hand_right_keypoints"]
                    else:
                        row += [0 for _ in xrange(21*3)]

                    wr.writerow(row)
            else:
                wr.writerow([group, subject, frame] + [0 for _ in xrange(390)])






