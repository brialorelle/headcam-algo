import os
import csv

TOTAL_POSE_POINTS = 18
TOTAL_FACE_POINTS = 70
TOTAL_HAND_POINTS = 21
CSV_OUTPUT_DIR = os.path.expandvars("$HOME/xs-face/scripts/openpose/tmp")
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/src/openpose/pose/poseParameters.cpp

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def body_part(num):
    return {
        0:  "Nose",
        1:  "Neck",
        2:  "RShoulder",
        3:  "RElbow",
        4:  "RWrist",
        5:  "LShoulder",
        6:  "LElbow",
        7:  "LWrist",
        8:  "RHip",
        9:  "RKnee",
        10: "RAnkle",
        11: "LHip",
        12: "LKnee",
        13: "LAnkle",
        14: "REye",
        15: "LEye",
        16: "REar",
        17: "LEar",
    }[num]

if __name__ == "__main__":

    with open(os.path.join(CSV_OUTPUT_DIR, "openpose_results.csv"), "wb") as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        header = ["group", "name", "frame"]

        for i, triple in enumerate(chunker(range(TOTAL_POSE_POINTS*3), 3)):
            prefix = body_part(i)
            header += [prefix + "_x", prefix + "_y", prefix + "_conf"]

        for i, triple in enumerate(chunker(range(TOTAL_FACE_POINTS*3), 3)):
            prefix = "face" + str(i)
            header += [prefix + "_x", prefix + "_y", prefix + "_conf"]

        for i, triple in enumerate(chunker(range(TOTAL_HAND_POINTS*3), 3)):
            prefix = "hand_left" + str(i)
            header += [prefix + "_x", prefix + "_y", prefix + "_conf"]

        for i, triple in enumerate(chunker(range(TOTAL_HAND_POINTS * 3), 3)):
            prefix = "hand_right" + str(i)
            header += [prefix + "_x", prefix + "_y", prefix + "_conf"]

        wr.writerow(header)

    # TODO name of these files? and then delete
    #os.system("cat {}/XS_* >> final_openpose_results.csv".format(CSV_OUTPUT_DIR))

