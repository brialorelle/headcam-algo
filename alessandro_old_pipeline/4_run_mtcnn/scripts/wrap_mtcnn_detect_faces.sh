#!/bin/sh

module load tensorflow
module load opencv/3.0.0

for vid_frames_dir in $PI_SCRATCH/samcam/rotated_frames/*; do
	sbatch -p hns,normal -c 8 -t 2:00:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
		    --wrap="python detect_faces.py $vid_frames_dir"
	sleep 1
done
