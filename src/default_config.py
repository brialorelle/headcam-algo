import os

SCRATCH = os.path.expandvars('$SCRATCH')

VID_NAMES = ['053113-1', '2013-10-27-part2', '061413-3',
             '2014-06-18-part2', '061713-1', '2014-01-01-part2']
VID_PATHS = [os.path.join(SCRATCH, 'testvideos', f'{vid_name}.AVI')
             for vid_name in VID_NAMES]

HOME_HEADCAM  = os.path.join(os.path.expandvars('$PI_SCRATCH'), 'Home_Headcam')
SAMCAM_VIDS = os.path.join(HOME_HEADCAM, 'Samcam', 'Videos')
ALICECAM_VIDS = os.path.join(HOME_HEADCAM, 'Alicecam', 'Videos')

NEW_SAM_VID_NAMES = []
NEW_SAM_VID_PATHS = [os.path.join(SAMCAM_VIDS, f'{vid_name}.AVI')
                     for vid_name in NEW_SAM_VID_NAMES]
NEW_ALICE_VID_NAMES = []
NEW_VID_NAMES = NEW_SAM_VID_NAMES + NEW_ALICE_VID_NAMES
NEW_ALICE_VID_PATHS = [os.path.join(ALICECAM_VIDS, f'{vid_name}.AVI')
                     for vid_name in NEW_ALICE_VID_NAMES]
NEW_VID_PATHS = NEW_SAM_VID_PATHS + NEW_ALICE_VID_PATHS

MASTER_JSON_PATH = os.path.join(SCRATCH, 'headcam-algo', 'gold_set.json')
SAMPLE_JSON_PATH = os.path.join(SCRATCH, 'headcam-algo', 'gold_set_sample.json')

OUTPUT = os.path.join(SCRATCH, 'headcam-algo', 'output')
OPENPOSE_OUTPUT = os.path.join(SCRATCH, 'headcam-algo', OUTPUT, 'openpose_json_output')
FRAME_DIRS = [os.path.join(OUTPUT, f'{vid_name}_frames') for vid_name in VID_NAMES]
