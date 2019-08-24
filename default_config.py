import os

VIDEO_DIRS = ['/scratch/groups/mcfrank/Home_Headcam_new/']
OUTPUT = '/scratch/users/agrawalk/headcam-algo-output/'
OPENPOSE_OUTPUT = os.path.join(OUTPUT, 'openpose')

GOLD_SET_NUM_FRAMES = 24000
# TODO: only include the user-facing constants here. 
# Move the path construction stuff to a utils helper

# SCRATCH = os.path.expandvars('$SCRATCH')

# VID_NAMES = ['053113-1', '2013-10-27-part2', '061413-3',
#              '2014-06-18-part2', '061713-1', '2014-01-01-part2']
# VID_PATHS = [os.path.join(SCRATCH, 'testvideos', f'{vid_name}.AVI')
#              for vid_name in VID_NAMES]

# DEMO_VID_PATH = '/scratch/users/agrawalk/demo/demovideo.mp4'
# DEMO_OUTPUT = '/scratch/users/agrawalk/demo/'

# NEW_SAM_VID_NAMES = []
# NEW_SAM_VID_PATHS = [os.path.join(SAMCAM_VIDS, f'{vid_name}.AVI')
#                      for vid_name in NEW_SAM_VID_NAMES]
# NEW_ALICE_VID_NAMES = []
# NEW_VID_NAMES = NEW_SAM_VID_NAMES + NEW_ALICE_VID_NAMES
# NEW_ALICE_VID_PATHS = [os.path.join(ALICECAM_VIDS, f'{vid_name}.AVI')
#                      for vid_name in NEW_ALICE_VID_NAMES]
# NEW_VID_PATHS = NEW_SAM_VID_PATHS + NEW_ALICE_VID_PATHS

# MASTER_JSON_PATH = os.path.join(SCRATCH, 'headcam-algo', 'gold_set.json')
# SAMPLE_JSON_PATH = os.path.join(SCRATCH, 'headcam-algo', 'gold_set_sample.json')

# FRAME_DIRS = [os.path.join(OUTPUT, f'{vid_name}_frames') for vid_name in VID_NAMES]
