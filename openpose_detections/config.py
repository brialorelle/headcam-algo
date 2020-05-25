import os
from default_config import *

#TODO: Change these from defaults (commented out)!

#List of directories containing videos in the dataset.
# VIDEO_DIRS = ['/scratch/groups/mcfrank/Home_Headcam_new/']

#Overall output directory.
OUTPUT = os.path.json(os.path.expandvars('$GROUP_SCRATCH'), 'outputs')

#Directory for raw Openpose output (warning: need inode space for millions of small JSON files)
OPENPOSE_OUTPUT = os.path.join(OUTPUT, 'openpose_raw_json')

#Directory for condensed Openpose output (one file per video) 
OPENPOSE_CONDENSED_OUTPUT = os.path.join(OUTPUT, 'openpose_condensed')

#File path for the video-level dataframe.
# VID_DATAFRAME_PATH = os.path.join(OUTPUT, 'master_vid_info.json')

#FIle path for the frame-level dataframe 
#(which will contain openpose outputs as well.)
# FRAME_DATAFRAME_PATH = os.path.join(OUTPUT, 'master_frames_openpose.h5')

#How much to rotate videos by (default 180, as most headcam videos are recorded upside down)
# VID_ROTATE = 180

#Dict from child id => birthdate in (year, month, day) format.
# BIRTHDATES = {'A': (YYYY, MM, DD), 'S': (YYYY, MM, DD)}

#Number of frames to extract for gold sample.
# GOLD_SET_NUM_FRAMES = 24000
