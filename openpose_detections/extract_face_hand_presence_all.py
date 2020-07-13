import os
import pandas as pd

from config import OPENPOSE_CONDENSED_OUTPUT
from openpose_helpers import extract_face_hand_presence

def extract_face_hand_presence_all(condensed_output_dir=OPENPOSE_CONDENSED_OUTPUT):
    condensed_files = os.listdir(condensed_output_dir)
    for i, vid_df_name in enumerate(condensed_files):
        print(f'{i+1}/{len(condensed_files)}: {vid_df_name}')
        vid_df_path = os.path.join(condensed_output_dir, vid_df_name)
        vid_df = pd.read_json(vid_df_path)
        if 'nose_conf' in vid_df and 'wrist_conf' in vid_df: 
            print('already extracted...continuing')
            continue
        vid_df = extract_face_hand_presence(vid_df)
        if vid_df is not None:
            vid_df.to_json(vid_df_path)
        del vid_df

if __name__ == '__main__':
    extract_face_hand_presence_all()
