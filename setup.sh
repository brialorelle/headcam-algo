#!/bin/bash

#TODO: add checks if stuff exists already
conda env create -f headcam.yml
conda activate headcam
#Do I need to create the Jupyter kernel here?

#One can create $SINGULARITY_CACHEDIR wherever it's convenient on your system.
mkdir $SCRATCH/.singularity
export SINGULARITY_CACHEDIR=$SCRATCH/.singularity
singularity pull docker://amsan7/openpose
