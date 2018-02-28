#!/bin/sh

vid_directory=/path/to/vid/directory

for vid in $vid_directory; do
	time=2:00:00
	memory=4G

	sbatch -p normal,hns -t $time --mem $memory --mail-type=FAIL --mail-user=sanchez7@stanford.edu \
	    --wrap="python helpers/json_to_csv.py $vid"
    sleep 1
done
