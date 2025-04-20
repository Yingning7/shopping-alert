#!/bin/bash

set -ex

CONDA_ENV_NAME="shopping-alert"
CONDA_REQUIREMENT_FILE="conda-requirements.txt"

conda create -n $CONDA_ENV_NAME --file "./bin/$CONDA_REQUIREMENT_FILE" -y
eval "$(conda shell.bash hook)"
conda activate $CONDA_ENV_NAME
pip install playwright
playwright install
