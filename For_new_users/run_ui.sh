#!/bin/bash

# Set up the environment
export PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export CONDA_EXE=/opt/anaconda3/bin/conda
export CONDA_PYTHON_EXE=/opt/anaconda3/bin/python
export CONDA_PREFIX=/opt/anaconda3
export CONDA_DEFAULT_ENV=QOL_env

# Activate the conda environment
source /opt/anaconda3/bin/activate QOL_env

# Run the Python script
/opt/anaconda3/bin/python $HOME/Downloads/QOL_Score/For_new_users/UI.py
