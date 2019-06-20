#!/bin/sh

conda env create -f environment.yml
mkdir $SCRATCH/.singularity 
export SINGULARITY_CACHEDIR=$SCRATCH/.singularity 
singularity pull docker://amsan7/openpose
