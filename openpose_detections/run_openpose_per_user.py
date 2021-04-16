# In[1]:
import os
import time
import pickle
import pandas as pd
from config import *
from run_openpose import run_openpose
from openpose_helpers import extract_face_hand_presence
# # Step 1: Run Openpose on videos
# In[2]:
#Edit these parameters in config.py
print('VID_ROTATE: ', VID_ROTATE)
print('OPENPOSE_OUTPUT: ', OPENPOSE_OUTPUT)
print('OPENPOSE_CONDENSED_OUTPUT: ', OPENPOSE_CONDENSED_OUTPUT)
"""Should be:
VID_ROTATE:  180
OPENPOSE_OUTPUT:  $GROUP_SCRATCH/Home_Headcam_new/outputs/openpose_raw_json
OPENPOSE_CONDENSED_OUTPUT:  $GROUP_SCRATCH/Home_Headcam_new/outputs/openpose_condensed
"""
# In[3]:
def run_openpose_on_vid_dir(vid_dir, op_output_dir=OPENPOSE_OUTPUT, condensed_output_dir=OPENPOSE_CONDENSED_OUTPUT, flipped_df_path=None):
    vid_files = os.listdir(vid_dir)
    vid_paths = [os.path.join(vid_dir, vid_name) for vid_name in vid_files]
    run_openpose_on_vid_list(vid_paths, op_output_dir, condensed_output_dir, flipped_df_path)

def run_openpose_on_vid_list(vid_list,  op_output_dir=OPENPOSE_OUTPUT, condensed_output_dir=OPENPOSE_CONDENSED_OUTPUT, flipped_df_path=None):
    for i, vid_path in enumerate(vid_list):
        print(f'{i+1}/{len(vid_list)}: {vid_path}')
        wait_for_space(15)
        run_openpose(vid_path, op_output_dir, 
                     frame_rotate=VID_ROTATE,
                     condensed_output_dir=condensed_output_dir,
                     keypoint_scale=3)

def wait_for_space(max_jobs):
    time.sleep(5) #Allow for squeue to refresh properly
    if queue_size() >= max_jobs:
        print('Waiting for space in queue...')
    while queue_size() >= max_jobs:
        time.sleep(600)

def queue_size():
    size = get_ipython().getoutput('squeue -u $USER')
    return len(size) - 1

# In[4]:
name = 'bria'  # bria, george
with open(f'/scratch/groups/mcfrank/Home_Headcam_new/vid_lists/op_list_{name}.p', 'rb') as f:
    vid_list = pickle.load(f)
# In[5]:
run_openpose_on_vid_list(vid_list, op_output_dir=OPENPOSE_OUTPUT, condensed_output_dir=OPENPOSE_CONDENSED_OUTPUT)