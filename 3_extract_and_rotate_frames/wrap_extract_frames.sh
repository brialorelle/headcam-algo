#!/bin/bash

for vid in $PI_SCRATCH/Home_Headcam/Alicecam/Videos/*.AVI; do
	echo $vid
	sbatch -p normal,hns -t 1:30:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
		 --wrap="python extract_frames.py $vid"
	sleep 1
done 
