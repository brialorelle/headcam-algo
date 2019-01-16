#!/bin/sh

module load cuda
module load py-tensorflow/1.4.0_py27
module load py-pillow/5.1.0_py27
module load opencv/3.3.0

# currently configured for face-detecting on the test videos.
for vid_frames_dir in $SCRATCH/headcam-algo/tests/output/*AVI; do
        echo "$vid_frames_dir"
	sbatch -p gpu --gres gpu:1 -c 8 -t 2:00:00 --mail-type=FAIL --mail-user=agrawalk@stanford.edu \
		    --wrap="python /scratch/users/agrawalk/headcam-algo/4_run_mtcnn/mtcnn/detect_faces.py $vid_frames_dir"
	sleep 1
done
