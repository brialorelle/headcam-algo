#!/bin/sh

for vid in $PI_SCRATCH/samcam/frames/*; do
	sbatch -p normal,hns -t 2:00:00 --mail-type=FAIL --mail-user=agrawalk@stanford.edu \
		   --wrap="python rotate_frames.py $vid"
	sleep 1
done
