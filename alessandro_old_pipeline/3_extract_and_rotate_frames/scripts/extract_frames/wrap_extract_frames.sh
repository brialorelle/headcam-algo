#!/bin/bash

for vid in $PI_SCRATCH/Home_Headcam/Alicecam/Videos/*; do
	echo $vid
	sbatch -p normal,hns -t 2:00:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
		 --wrap="python extract_frames.py $vid"
	sleep 1
done 
