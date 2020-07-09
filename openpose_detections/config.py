import os
from default_config import *

# TODO: Change these from defaults (commented out)!

# List of directories containing videos in the dataset
# (i.e. the ones you downloaded with download_databrary_volume.py --
#  note that this may just be one directory in the list).
# VIDEO_DIRS = ['/scratch/groups/mcfrank/Home_Headcam_new/Alicecam',
#               '/scratch/groups/mcfrank/Home_Headcam_new/Samcam',
#               '/scratch/groups/mcfrank/Home_Headcam_new/Asacam']

# Overall output directory.
# OUTPUT = os.path.join(os.path.expandvars('$GROUP_SCRATCH'), 'Home_Headcam_new', 'outputs')

# Directory for raw Openpose output (warning: need inode space for millions of small JSON files)
# OPENPOSE_OUTPUT = os.path.join(OUTPUT, 'openpose_raw_json')

# Directory for condensed Openpose output (one file per video)
# OPENPOSE_CONDENSED_OUTPUT = os.path.join(OUTPUT, 'openpose_condensed')

# How much to rotate videos by (default 180, as most headcam videos are recorded upside down)
# VID_ROTATE = 180

# Dict from child id => birthdate in (year, month, day) format.
# BIRTHDATES = {'A': (YYYY, MM, DD), 'S': (YYYY, MM, DD), 'Y': (YYYY, MM, DD)}

# Number of frames to extract for gold sample.
# GOLD_SET_NUM_FRAMES = 24000
