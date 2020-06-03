#!/usr/bin/env bash
# Sets up conda environment and pulls Openpose Singularity container into specified directory.
# If no install directory is provided, Openpose will be installed in $HOME
# (WARNING: takes up 2GB)
# This script should be run from a development node, not a login node.
# Example usage: chmod +x setup.sh; ./setup.sh /path/to/desired/openpose_install_dir

# #Create Conda env
echo "Initializing conda for bash shell..."
conda init

echo "Creating conda env..."
conda env create -f headcam.yml
conda activate headcam
echo "Installing ipython kernel..."
python -m ipykernel install --user --name headcam --display-name "Python (headcam)"

echo "Installing Openpose Singularity container in ${1:-$HOME}/.singularity ..."
export SINGULARITY_CACHEDIR=${1:-$HOME}/.singularity
mkdir $SINGULARITY_CACHEDIR
singularity pull docker://amsan7/openpose
