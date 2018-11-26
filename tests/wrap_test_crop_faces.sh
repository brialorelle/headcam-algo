#!/bin/sh
# wrapper script for test cropping faces.
module load opencv/3.3.0
module load py-pandas/0.23.0_py27

sbatch -p normal,hns -t 2:00:00 --mail-type=FAIL --mail-user=agrawalk@stanford.edu \
                     --wrap="python test_crop_faces.py"
