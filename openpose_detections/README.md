# Openpose Detections

First, ensure you have completed the setup in https://github.com/brialorelle/headcam-algo/#getting-started.

To setup headcam analysis, edit [config.py](config.py) to specify project-level parameters, such as output directories and filenames. The default values for these variables (and some more constants) are defined in [default_config.py](default_config.py).

NB: If on a computing cluster, it is recommended to use your scratch space for OUTPUT due to the size and numerosity of outputs.

In order to run the Jupyter notebooks in this directory, ensure that you have the `headcam` conda environment active (which has JupyterLab installed), then run `jupyter lab` from the command line. A link to copy and paste in the browser should appear. (If running on a remote machine, you may need to port-forward this back to your own machine; [this tutorial](https://vsoch.github.io/lessons/sherlock-jupyter/) may be helpful, especially if running on Sherlock or a similar computing cluster.)

To test out openpose on some demo videos and get some intuition about what the openpose outputs look like, run through the code in the notebook [openpose_pipeline_demo.ipynb](openpose_pipeline_demo.ipynb). 

Finally, to run openpose on the full dataset, run through the code in the notebook [openpose_pipeline.ipynb](openpose_pipeline.ipynb). 
