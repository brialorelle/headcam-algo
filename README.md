# A longitudinal analysis of the social information in infants' naturalistic visual experience using automated detections

## Reproducing analysis in the submission 

The main analyses and writeup for the paper are in the paper/preprint/manuscript_june2021_apa_blinded.Rmd. 
Data for the paper can be found at https://osf.io/cdhw4/ in data_preprocessed_2021.zip; this folder should be unzipped and placed in the main directory/data. 

1. OpenPose detections were obtained using the pipeline outlined below (openpose_detections/openpose_pipeline.ipynb). 
2. Bounding boxes were extracted using preprocessing/2_get_bounding_boxes_per_vid.py and preprocessing/step3_merge_per_vid_bounding_boxes.R
3. Human annotations for faces/hands obtained using AMT; basic preprocessing is in preprocessing/step0_get_human_annotations/face_hands/analysis a
4. Detections were preprocessed and joined with metadata to create intermediate data files, using preprocessing/step4_create_bounding_box_summaries.Rmd and preprocessing/step5_preprocess_fullset_from_bb_outputs.Rmd


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

Next, make `setup.sh` executable and run it to setup the conda environment and pull the openpose docker into a location with at least 2GB of space:
```
chmod +x setup.sh
./setup.sh /path/to/desired/openpose_install_dir
```

### Download Dataset

With the `headcam` conda environment active, run the [download_databrary_volume.py](misc/download_databrary_volume.py) script to download volume 564 on databrary, "Head cameras on children aged 6 months through 31 months", and then run [clean_video_repo.sh](misc/clean_video_repo.sh) to format the filenames properly and remove extraneous, non-video files: 

You will need roughly 500GB of space to download this volume.

```
python misc/download_databrary_volume.py 564 -o /path/to/desired/video_download_dir
chmod +x ./misc/clean_video_repo.sh
./misc/clean_video_repo.sh /path/to/desired/video_download_dir
```

(In order to download a different Databrary dataset, simply specify the appropriate volume number for that dataset. `clean_video_repo.sh` is not intended for use on other datasets.)

## Analysis

Follow the instructions in the [README](openpose_detections/README.md) in the `openpose_detections` folder in order to run Openpose on all the videos in the dataset and save outputs in CSV format.

