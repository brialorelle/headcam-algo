import os

#List of directories containing videos in the dataset.
VIDEO_DIRS = ['/scratch/groups/mcfrank/Home_Headcam_new/']

#Overall output directory.
OUTPUT = '/Users/brialong/Documents/GitHub/headcam-algo/data'


# OUTPUT = '/scratch/users/agrawalk/headcam-algo-output/'

# see https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md
OPENPOSE_NUM_POSE_KEYPTS = 18
OPENPOSE_NUM_FACE_KEYPTS = 70
OPENPOSE_NUM_LEFT_HAND_KEYPTS = 21
OPENPOSE_NUM_RIGHT_HAND_KEYPTS = 21
OPENPOSE_NUM_KEYPTS = OPENPOSE_NUM_POSE_KEYPTS + \
    OPENPOSE_NUM_FACE_KEYPTS + \
    OPENPOSE_NUM_LEFT_HAND_KEYPTS + \
    OPENPOSE_NUM_RIGHT_HAND_KEYPTS # i.e. 130 keypts

OPENPOSE_FACE_NOSE_KEYPT = 30
OPENPOSE_POSE_LEFT_WRIST_KEYPT = 7
OPENPOSE_POSE_RIGHT_WRIST_KEYPT = 4

NPY_POSE_START = 0
NPY_POSE_END = NPY_FACE_START = 18
NPY_FACE_END = NPY_HAND_LEFT_START = 88
NPY_HAND_LEFT_END = NPY_HAND_RIGHT_START = 109
NPY_HAND_RIGHT_END = 130

#Directory for raw Openpose output (warning: need inode space for millions of small JSON files)
OPENPOSE_OUTPUT = os.path.join(OUTPUT, 'openpose')

#Directory for condensed Openpose output (one file per video) 
OPENPOSE_CONDENSED_OUTPUT = os.path.join(OUTPUT, 'openpose_condensed')

#File path for the video-level dataframe.
VID_DATAFRAME_PATH = os.path.join(OUTPUT, 'master_vid_info.json')

#File path for the frame-level dataframe
#(which will contain openpose outputs as well.)
FRAME_DATAFRAME_PATH = os.path.join(OUTPUT, 'master_frames_openpose.h5')

#FIle path for the gold sample of frames used to evaluate detector performance.
SAMPLE_DATAFRAME_PATH = os.path.join(OUTPUT, 'gold_sample.json')

#How much to rotate videos by (default 180, as most headcam videos are recorded upside down)
VID_ROTATE = 180

#Dict from child id => birthdate in (year, month, day) format.
#NOTE: Actual birthdates not included for privacy reasons.
BIRTHDATES = {'A': (1980, 1, 1), 'S': (1980, 1, 1)}

#Number of frames to extract for gold sample.
GOLD_SET_NUM_FRAMES = 24000
