# Openpose Detections

First, ensure you have completed the setup in https://github.com/brialorelle/headcam-algo/#getting-started.

To setup headcam analysis, edit [config.py](config.py) to specify project-level parameters, such as output directories and filenames. The default values for these variables (and some more constants) are defined in [default_config.py](default_config.py).

NB: If on a computing cluster, it is recommended to use your scratch space for OUTPUT due to the size and numerosity of outputs.

To test out openpose on some demo videos and get some intuition about what the openpose outputs look like, run through the code in the notebook [openpose_pipeline_demo.ipynb](openpose_pipeline_demo.ipynb). 

Finally, to run openpose on the full dataset, run through the code in the notebook [openpose_pipeline.ipynb](openpose_pipeline.ipynb). 
