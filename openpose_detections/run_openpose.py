#!/usr/bin/env python3

import argparse
import os
import ntpath

from utils import submit_job
from config import *


def run_openpose(vid_path, op_output_dir, face=True, hand=True,
                 overwrite=False, condense=True, condensed_output_dir=OPENPOSE_CONDENSED_OUTPUT, **kwargs):
    """run_openpose: submit sbatch job to run Openpose on given video.

    :param vid_path: path to video file.
    :param op_output_dir: directory that will house Openpose output folders.
    :param face: outputs face keypoints (in addition to pose keypoints) if True.
    :param hand: outputs hand keypoints (in addition to pose keypoints) if True.
    :param overwrite: if True, overwrites existing openpose output folders.
    :param condense: if True, condenses openpose outputs into a single dataframe.
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
        if not overwrite:
            print(f'Outputs already exist for video {vid_path} -- continuing...')
            return
        else:
            print(f'NOTE: overwriting data in {vid_output_dir}')

    # this could also be openpose_latest.sif, instead of openpose-latest.img.
    cmd = 'singularity exec --nv $SINGULARITY_CACHEDIR/openpose-latest.sif bash -c \''
    cmd += 'cd /openpose-master && ./build/examples/openpose/openpose.bin '
    cmd += f'--no_display true '
    cmd += f'--render_pose 0 '
    cmd += f'--video {vid_path} '
    for opt, optval in kwargs.items():
        cmd += f'--{opt} {optval} '
    if face:
        cmd += '--face '
    if hand:
        cmd += '--hand '
        cmd += f'--write_keypoint_json {vid_output_dir}\''
    if condense:  # After Openpose command completes, condense into single JSON
        save_path = os.path.join(condensed_output_dir, vid_name + '.json')
        cmd += f' && python condense_openpose_output.py {vid_output_dir} -o {save_path}'

    msg = submit_job(cmd, job_name=f'{vid_name}', p='gpu,hns', t=5.0, mem='8G', gres='gpu:1')
    print(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Submit a job to run'
                                     'openpose binary on a video.')
    parser.add_argument('vid_path', metavar='PATH', type=str,
                        help='path to video to run openpose on')
    parser.add_argument('--output_dir', '-o', type=str, default=OPENPOSE_OUTPUT,
                        help='Directory in which to create the Openpose output directory')
    parser.add_argument('--condense', type=bool, default=True,
                        help='If set, condenses outputs into a single JSON dataframe')
    args = parser.parse_args()
    run_openpose(args.vid_path, args.output_dir, condense=args.condense)
