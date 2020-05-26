#!/usr/bin/env bash

# reformats any extraneous videos in provided directory with .AVI.mp4 ending to .mp4 ending
# removes any files that are not headcam videos
# Example usage: chmod +x ./clean_video_repo.sh; ./clean_video_repo.sh /path/to/video/repo

for file in $1/*AVI.mp4; do mv "$file" "${file%.AVI.mp4}.mp4" 2>/dev/null; done
for file in $1/*mov.mp4; do mv "$file" "${file%.mov.mp4}.mp4" 2>/dev/null; done
shopt -s extglob
rm $1/!(A_*.mp4|S_*.mp4|Y_*.mp4) 2>/dev/null 

