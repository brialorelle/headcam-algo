#!/usr/bin/env python3

import time
import argparse
import os
import subprocess
import ntpath

from utils import submit_job
from config import *

from openpose_helpers import create_video_dataframe

def run_openpose(vid_path, op_output_dir, face=True, hand=True,
                 overwrite=False, condense=True, **kwargs):
    """run_openpose: submit sbatch job to run Openpose on given video.

    :param vid_path: path to video file.
    :param op_output_dir: directory that will house Openpose output folders.
    :param face: outputs face keypoints (in addition to pose keypoints) if True.
    :param hand: outputs hand keypoints (in addition to pose keypoints) if True.
    :param **kwargs: additional command-line arguments to pass to Openpose
    (see https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/demo_overview.md
    for complete documentation on command-line flags).

    Example usage:
    run_openpose('/path/to/myheadcamvid.mp4', '/path/to/output_dir',
                 keypoint_scale=3, frame_rotate=180)
    """
    os.makedirs(op_output_dir, exist_ok=True)
    vid_name = ntpath.basename(vid_path)[:-4]
    vid_output_dir = os.path.join(op_output_dir, f'{vid_name}')

    if os.path.exists(vid_output_dir):
        if not overwrite and input(f'overwrite existing directory {vid_output_dir}? (yes/no)') != 'yes':
            print(f'aborting on video {vid_path}.')
            return
        os.makedirs(vid_output_dir, exist_ok=True)

    #this could also be openpose_latest.sif, instead of openpose-latest.img.
    cmd = 'singularity exec --nv $SINGULARITY_CACHEDIR/openpose-latest.img bash -c \''
    cmd += 'cd /openpose-master && ./build/examples/openpose/openpose.bin '
    cmd += f'--video {vid_path} '
    for opt, optval in kwargs.items():
        cmd += f'--{opt} {optval} '
    if face:
        cmd += '--face '
    if hand:
        cmd += '--hand '
        cmd += f'--write_keypoint_json {vid_output_dir}\''
        # print('command submitted to sbatch job: ', cmd)

    msg = submit_job(cmd, job_name=f'{vid_name}', p='gpu', t=5.0, mem='8G', gres='gpu:1')
    print(msg)

    if condense:
        def job_exists(vid_name):
            jobs = subprocess.check_output(['sacct' '--format', "JobName%30"])
            return vid_name in jobs

        print('Waiting for job to finish...')
        while job_exists(vid_name):
            time.sleep(100)
        print('Job finished - condensing outputs into single JSON file...')
        create_video_dataframe(vid_output_dir, save_path=op_output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download a volume from databrary.')
    # defaults to volume 564, Sullivan et al. headcam dataset
    parser.add_argument('vid_path', metavar='PATH', type=str,
                        help='path to video to run openpose on')
    parser.add_argument('--output_dir', '-o', type=str, default=OPENPOSE_OUTPUT,
                        help='Directory in which to create the Openpose output directory')
    parser.add_argument('--condense', type=bool, default=True,
                        help='If set, condenses outputs into a single JSON dataframe')
    args = parser.parse_args()
    run_openpose(args.vid_path, args.output_dir, condense=args.condense)
