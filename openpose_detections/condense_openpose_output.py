#!/usr/bin/env python3

import time
import subprocess
import argparse

from openpose_helpers import create_video_dataframe

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Condense Openpose output for a '
                                     'given video into one JSON file')
    parser.add_argument('vid_output_dir', metavar='DIR', type=str,
                        help='Directory from which to extract JSONs '
                        'to create the condensed Openpose JSON')
    parser.add_argument('--save_path', '-o', type=str,
                        help='Path into which to save the condensed Openpose JSON')
    args = parser.parse_args()

    create_video_dataframe(args.vid_output_dir, save_path=args.save_path)
