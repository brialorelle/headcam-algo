"""
Script to extract frames from a video w/ ffmpeg to a folder.
Currently configured for testing.
"""
# NOTE: when running, check if images have successfully been flipped
# by ffmpeg. If so, no need to run the rotate_frames code.

import ntpath
import os
import sys

HOME_DIR = os.path.expandvars("$SCRATCH")
OUT_DIR = os.path.join(HOME_DIR, 'headcam-algo/tests/output')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)


if __name__ == "__main__":
    full_filename = sys.argv[1]
    video_name = ntpath.basename(full_filename)
    video_dir_name = os.path.join(OUT_DIR, video_name)
    if not os.path.exists(video_dir_name):
        os.makedirs(video_dir_name)
    cmd = 'ffmpeg -i {0} -vf "hflip,vflip,scale=720:480" -vsync 0 {1}'\
        .format(full_filename, os.path.join(video_dir_name, 'image-%5d.jpg'))
    os.system(cmd)
