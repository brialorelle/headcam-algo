#!/bin/sh

sbatch -p normal,hns -t 1:30:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
	--wrap="ffmpeg -i $PI_HOME/samcam/010415-1\ 2.AVI -vf \"hflip,vflip,scale=720:480\" -vsync 0 $PI_HOME/samcam/samcam_sample_frames/image-%5d.jpg"
