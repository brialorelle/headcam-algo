import os
import sys
import ntpath

OUTPUT_DIR = os.path.expandvars("$PI_HOME/samcam/frames4")
# TODO on old sherlock this may be different
#FFMPEG_BIN = os.path.expandvars("$HOME/ffmpeg-3.4-64bit-static/ffmpeg")


if __name__ == "__main__":
    full_filename = sys.argv[1]
    video_name = ntpath.basename(full_filename)
    video_dir_name = os.path.join(OUTPUT_DIR, video_name)
    os.system('mkdir {0}'.format(video_dir_name))
    cmd = 'ffmpeg -i {0} -vf "hflip,vflip,scale=720:480" -vsync 0 {1}/image-%5d.jpg'\
        .format(full_filename, video_dir_name)
    os.system(cmd)

