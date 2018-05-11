# pip install Pillow if you don't already have it

# import image utilities
from PIL import Image

# import os / sys utilities
import os
import sys
import ntpath
# folder arg is frames3

#OUT_DIR = os.path.expandvars("$PI_HOME/frames4")
# TMP
OUT_DIR = os.path.expandvars("$PI_HOME/samcam/frames_rotated")

# define a function that rotates images in the current directory
# given the rotation in degrees as a parameter
def rotateImages(folder):
    print(folder)
    vid = ntpath.basename(folder)
    os.system("mkdir {}".format(os.path.join(OUT_DIR, vid)))

    for image in os.listdir(folder):
        img = Image.open(os.path.join(folder, image))
        img.rotate(180).save(os.path.join(OUT_DIR, vid, image))
        img.close()

if __name__ == "__main__":
    rotateImages(sys.argv[1])

