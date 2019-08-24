import os
from default_config import *

#TODO: move these to default config, make these placeholders that the user has to fill in.
#Only include the placeholders here for the stuff that the user has to specify.
#Include the placeholders commented out, with stuff that they should be defining themselves.
#Write comments describing what each parameter means.

# VIDEO_DIRS = ['/scratch/groups/mcfrank/Home_Headcam_new/']
VIDEO_DIRS = ['/scratch/users/agrawalk/pipeline_test_vids/']
OUTPUT = '/scratch/users/agrawalk/headcam-algo-output/'
OPENPOSE_OUTPUT = os.path.join(OUTPUT, 'openpose')
OPENPOSE_CONDENSED_OUTPUT = os.path.join(OUTPUT, 'openpose_condensed')

GOLD_SET_NUM_FRAMES = 24000
BATCH_SIZE = 1000
VID_ROTATE = 180

# old stuff.
# DEMO_VID_PATH = '/scratch/users/agrawalk/demo/demovideo.mp4'
# DEMO_OUTPUT = '/scratch/users/agrawalk/demo/'

# HOME_HEADCAM  = os.path.join(os.path.expandvars('$PI_SCRATCH'), 'Home_Headcam_new')
# SAMCAM_VIDS = os.path.join(HOME_HEADCAM, 'Samcam')
# ALICECAM_VIDS = os.path.join(HOME_HEADCAM, 'Alicecam')

# NEW_VID_PATHS = ['/scratch/users/agrawalk/demovideo.mp4']
