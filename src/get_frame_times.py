# Count frames with ffprobe 3.4 taking .mov as input argument

import os
import csv
from config import *

OUTPUT_FILE = os.path.expandvars("$HOME/headcam-algo/src/ffprobe_frame_count.csv")

CMD = "ffprobe " \
      "-v error " \
      "-count_frames " \
      "-select_streams v:0 " \
      "-show_entries stream=nb_read_frames " \
      "-of default=nokey=1:noprint_wrappers=1 " \
      "%s"

if __name__ == "__main__":

    with open(OUTPUT_FILE, 'wb') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(["video", "num_frames"])

        for root, _, filenames in os.walk(ALICECAM_VIDS):
            for video in filenames:
                video_path = os.path.join(root, video)
                num_frames = os.popen(CMD % video_path).read()
                wr.writerow(['_'.join(video.split('_')[:2]), int(num_frames)])
                f.flush()

        for root, _, filenames in os.walk(SAMCAM_VIDS):
            for video in filenames:
                video_path = os.path.join(root, video)
                num_frames = os.popen(CMD % video_path).read()
                wr.writerow(['_'.join(video.split('_')[:2]), int(num_frames)])
                f.flush()
