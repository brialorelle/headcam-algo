
import os
import ujson
import multiprocessing as mp
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections as mc

from config import *
from openpose_helpers import *
from run_openpose_test import run_openpose_test

OUTPUT ='/scratch/groups/mcfrank/daylight'



DEMO_OUTPUT = os.path.join(OUTPUT, 'op_output')
demo_vid_path = os.path.join(OUTPUT, 'Faces.MP4')

op_output_dir = os.path.join(DEMO_OUTPUT, 'openpose_raw_json')
condensed_output_dir = os.path.join(DEMO_OUTPUT, 'openpose_condensed')

run_openpose_test(demo_vid_path, op_output_dir, 
             condensed_output_dir=condensed_output_dir, 
             keypoint_scale=3, condense=True, overwrite=False)