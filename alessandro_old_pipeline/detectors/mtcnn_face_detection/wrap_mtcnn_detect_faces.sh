#!/bin/sh

module load tensorflow
module load opencv/3.0.0

frame_directory=/path/to/frames

for vid in $frame_directory; do
	sbatch -p hns,normal -c 8 -t 10:00:00 --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
		--wrap="python detect_faces.py $vid"
	sleep 1
done
