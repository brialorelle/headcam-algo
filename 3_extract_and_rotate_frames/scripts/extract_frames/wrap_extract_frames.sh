#!/bin/bash

module load ffmpeg

for vid in $HOME/testvideos/*; do
	echo $vid
	sbatch -p normal,hns -t 2:00:00 --mail-type=FAIL --mail-user=agrawalk@stanford.edu \
		 --wrap="python extract_frames.py $vid"
	sleep 1
done 
