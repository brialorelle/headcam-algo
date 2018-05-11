#!/bin/bash
# creates a one line csv for every video folder, documenting total number of frames outputted 
# ls -f for fast, unordered list. this always includes . and .., so then need to subtract it out

for vid in $PI_SCRATCH/samcam/frames/*; do
        echo $vid
	c=$(ls -f $vid | wc -l) && echo $(basename $vid),$(($c - 2)) > tmp/$(basename $vid).txt
done

echo "\"video\",\"num_frames\"" > frames_counted.csv
cat tmp/*.txt >> frames_counted.csv
