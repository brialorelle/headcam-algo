
# Detecting social information in a dense dataset of infants’ natural visual experience

## Reproducing CogSci2020 

The main analyses and writeup for the paper are in the paper/cogsci folder. Data for the paper can be found at https://osf.io/cdhw4/ at 
data_cogsci.zip; this folder should be unzipped and placed in the main directory.

1. OpenPose detections were obtained using the pipeline outlined below (openpose_detections/openpose_pipeline.ipynb). 
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

Next, run `setup.sh` to setup the conda environment and pull the openpose docker into a location with at least 2GB of space:
```
chmod +x setup.sh
./setup.sh /path/to/desired/openpose_install_dir
```

### Download Dataset

With the `headcam` conda environment active, use the [download_databrary_volume.py](misc/download_databrary_volume.py) script to download volume 564 on databrary, "Head cameras on children aged 6 months through 31 months", and [clean_video_repo.sh](misc/clean_video_repo.sh) to format the filenames properly and remove extraneous, non-video files:

You will need roughly 500GB of space to download this volume.

```
python misc/download_databrary_volume.py 564 -o /path/to/desired/video_download_dir
chmod +x ./misc/clean_video_repo.sh
./misc/clean_video_repo.sh /path/to/desired/video_download_dir
```

(In order to download a different Databrary dataset, simply specify the appropriate volume number for that dataset. `clean_video_repo.sh` is not intended for use on other datasets.)

## Analysis

Follow the instructions in the [README](openpose_detections/README.md) in the `openpose_detections` folder in order to run Openpose on all the videos in the dataset and save outputs in CSV format.

TODO: describing bounding box code, gold sample annotation, etc.

## Contributors

* **Bria Long**
* **Ketan Agrawal**
* **George Kachergis**
* **Alessandro Sanchez** - *Initial work* - [xs-face](https://github.com/amsan7/xs-face)

