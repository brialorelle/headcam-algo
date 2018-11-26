"""
Script to rotate upside-down frames from a folder.
Currently configured for testing.
"""

# pip install Pillow if you don't already have it

import ntpath
# import os / sys utilities
import os
import sys

# import image utilities
from PIL import Image

# folder arg is frames3

# OUT_DIR = os.path.expandvars("$PI_HOME/frames4")
# TMP
HOME_DIR = '/scratch/users/agrawalk/'
OUT_DIR = os.join(HOME_DIR, 'headcam-algo/tests/output')
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

# define a function that rotates images in the current directory
# given the rotation in degrees as a parameter


def rotateImages(folder):
    print(folder)
    vid = ntpath.basename(folder)
    os.makedirs(os.path.join(OUT_DIR, vid))

    for image in os.listdir(folder):
        img = Image.open(os.path.join(folder, image))
        img.rotate(180).save(os.path.join(OUT_DIR, vid, image))
        img.close()


if __name__ == "__main__":
    rotateImages(sys.argv[1])
