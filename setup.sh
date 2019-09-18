#!/bin/bash

#Create Conda env
echo "Creating conda env..."
conda env create -f headcam.yml
source activate headcam
python -m ipykernel install --user --name headcam --display-name "Python (headcam)"

#Pull Openpose Docker
#TODO: change this to wherever is convenient, i.e. /path/to/.singularity.
echo "Pulling Openpose Docker..."
mkdir $SCRATCH/.singularity
#One can create $SINGULARITY_CACHEDIR wherever it's convenient on your system.
export SINGULARITY_CACHEDIR=$SCRATCH/.singularity
singularity pull docker://amsan7/openpose
