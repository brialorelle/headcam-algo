import numpy as np
import pandas as pd
from openpose_helpers import create_video_dataframe
from openpose_helpers import recover_npy
import os
#input_dir = "/scratch/groups/mcfrank/Home_Headcam_new/outputs/openpose_raw_json_Y"
#output_dir = "/scratch/groups/mcfrank/Home_Headcam_new/openpose_condensed_Y/"
#npy_output_dir = "/scratch/groups/mcfrank/Home_Headcam_new/openpose_flattened_Y/"

input_dir = "/scratch/groups/mcfrank/Home_Headcam_new/outputs/openpose_condensed_SA"
npy_output_dir = "/scratch/groups/mcfrank/Home_Headcam_new/outputs/openpose_flattened"

vid_dirs = os.listdir(input_dir)


for vid in vid_dirs:
	print("Processing " + vid)
	out_path = os.path.join(npy_output_dir, os.path.splitext(vid)[0]+'.npy')
	# don't re-export if already exists
	if not os.path.exists(out_path):
		# for per-frame JSON files:
	    #vid_df = create_video_dataframe(os.path.join(input_dir, vid), save_path=os.path.join(output_dir, vid+'.json'))
	    # for per-video JSON files:
	    vid_df = pd.read_json(os.path.join(input_dir, vid))
	    vid_npy = recover_npy(vid_df)
	    np.save(out_path, vid_npy)
