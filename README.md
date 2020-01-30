
# Detecting social information in a dense dataset of infants’ natural visual experience

## Reproducing CogSci2020 

The main analyses and writeup for the paper are in the paper/cogsci folder. Data for the paper can be found at https://osf.io/cdhw4/ at 
data_cogsci.zip; this folder should be unzipped and placed in the main directory.

1. OpenPose detections were obtained using the pipeline outlined below (openpose_detections/openpose.ipynb). 
2. Bounding boxes were extracted using preprocessing/get_bounding_boxes_per_vid.py and preprocessing/get_all_openpose_bounding_boxes.R
3. Human annotations for faces/hands obtained using AMT; basic preprocessing is in human_annotatiions/face_hands/analysis and in preprocessing/preprocess_datasets.Rmd
4. Detections were preprocessed and joined with metadata to create intermediate data files, using preprocessing/preprocess_datasets.Rmd


# Running OpenPose Detections 

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

To setup headcam analysis, edit [config.py](openpose_detections/config.py) to specify project-level parameters, such as output directories and filenames. (if on a computing cluster, it is recommended to use your SCRATCH space for OUTPUT due to the size and numerosity of outputs.)

Then, run through the code in [setup_dataframes.ipynb](openpose_detections/setup_dataframes.ipynb) to create and save Pandas dataframes containing information for each video and each frame in your dataset.

To run Openpose on the entire dataset and condense the outputs run through the code in [openpose.ipynb](openpose_detections/openpose.ipynb). 

To hand-annotate a random sample of frames from the dataset for presence of face and hand and to check the precision, recall, and F-score of Openpose with respect to those human annotations, run through the code in [detector_validation.ipynb](openpose_detections/detector_validation.ipynb) (Note: annotation script is not likely to work on Sherlock; instead, copy the sample images and clone to repo to your local machine and annotate there.)

## Contributors

* **Bria Long**
* **Ketan Agrawal**
* **George Kachergis**
* **Alessandro Sanchez** - *Initial work* - [xs-face](https://github.com/amsan7/xs-face)

