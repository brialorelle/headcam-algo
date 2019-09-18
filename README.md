# Headcam Analysis

This repository contains code designed to run on infant headcam videos at scale, using the [Openpose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) pose detector to extract information about facial and manual cues in the infants' environments.

## Getting Started

This repository was made to run on the Sherlock computing cluster at Stanford. As such, some analysis steps rely on the Slurm Workload Manager to submit compute-intensive jobs. You may need to modify the job submission code if you are running on a different cluster.

### Prerequisites

You should have [conda](https://docs.conda.io/en/latest/miniconda.html) and [Singularity](https://github.com/sylabs/singularity) installed on your machine.

### Installing

Here's what's needed to setup the project.

Clone the repo:
```
git clone https://github.com/brialorelle/headcam-algo.git
cd headcam-algo/
```

Next, edit `setup.sh` (the line below TODO) to install the `.singularity` directory where it is desired. Run the setup script, which creates the conda environment, installing the requisite python packages, and pulls the Openpose docker:
```
chmod +x setup.sh
./setup.sh
```

## Analysis

To setup headcam analysis, edit [config.py](src/config.py) to specify project-level parameters, such as output directories and filenames. (if on a computing cluster, it is recommended to use your SCRATCH space for OUTPUT due to the size and numerosity of outputs.)

Then, run through the code in [setup_dataframes.ipynb](src/setup_dataframes.ipynb) to create and save Pandas dataframes containing information for each video and each frame in your dataset.

To run Openpose on the entire dataset and condense the outputs run through the code in [openpose.ipynb](src/openpose.ipynb). 

To hand-annotate a random sample of frames from the dataset for presence of face and hand and to check the precision, recall, and F-score of Openpose with respect to those human annotations, run through the code in [detector_validation.ipynb](src/detector_validation.ipynb) (Note: annotation script is not likely to work on Sherlock; instead, copy the sample images and clone to repo to your local machine and annotate there.)

For various visualizations of the dataset such as plotting the presence of faces and hands over time, run through the code in [face_hand_trends.ipynb](src/face_hand_trends.ipynb).

## Contributors

* **Ketan Agrawal**
* **Alessandro Sanchez** - *Initial work* - [xs-face](https://github.com/amsan7/xs-face)

