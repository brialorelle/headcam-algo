#!/bin/bash

for vid in $PI_SCRATCH/Home_Headcam/Alicecam/Videos/*.AVI; do
	sbatch -p normal,hns -t 35:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
        --wrap="ffprobe -show_frames -select_streams v:0 $vid > data/$(basename $vid).frames.txt"
	sleep 1
done
