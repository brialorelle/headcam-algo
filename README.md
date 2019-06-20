# Headcam Analysis

Repository for running face/pose detectors on infant headcam videos, and evaluating the precision, recall, and F-score of said detectors.

## Getting Started

### Prerequisites

You should have [conda](https://docs.conda.io/en/latest/miniconda.html) and [Singularity](https://github.com/sylabs/singularity) installed on your machine.

```
Give examples
```

### Installing

Here's what's needed to setup the project.

Clone the repo:
```
git clone https://github.com/brialorelle/headcam-algo.git
cd headcam-algo/
```

Run the setup script, which creates the python environment and pulls the Openpose docker:
```
./setup.sh
```

## Running the analysis

At a terminal, enter `jupyter notebook`, and open `gold_set_eval.ipynb`. Run the cells of this notebook to extract frames from a video, run detectors/hand-annotate on a sample, and analyze the detectors' precision, recall, and F1 score.

## Contributors

* **Ketan Agrawal**
* **Alessandro Sanchez** - *Initial work* - [xs-face](https://github.com/amsan7/xs-face)

