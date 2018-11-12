#!/bin/sh

module load py-tensorflow/1.4.0_py27
module load py-pillow/5.1.0_py27
module load opencv/3.3.0

for vid_frames_dir in $SCRATCH/testvid_rotated; do
	sbatch -p gpu --gres gpu:1 -c 8 -t 2:00:00 --mail-type=FAIL --mail-user=agrawalk@stanford.edu \
		    --wrap="python /scratch/users/agrawalk/samcam/4_run_mtcnn/mtcnn/detect_faces_simple.py $vid_frames_dir"
	sleep 1
done
