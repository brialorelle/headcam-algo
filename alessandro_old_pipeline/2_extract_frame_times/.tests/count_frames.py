# Count frames with ffprobe 3.4 taking .mov as input argument

import os
import csv

MOVIE_DIR = os.path.expandvars("$PI_SCRATCH/Home_Headcam/Alicecam/Videos/")
OUTPUT_FILE = os.path.expandvars("./ffprobe_frame_count.csv")

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

        for root, _, filenames in os.walk(MOVIE_DIR):
            for video in filenames:
                video_path = os.path.join(root, video)
                num_frames = os.popen(CMD % video_path).read()
                wr.writerow([video, int(num_frames)])
                f.flush()
