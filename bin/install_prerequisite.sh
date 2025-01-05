#!/bin/bash

CONDA_ENV_NAME="shopping-alert"
CONDA_REQUIREMENT_FILE="conda-requirements.txt"

conda create -n $CONDA_ENV_NAME --file "./bin/$CONDA_REQUIREMENT_FILE" -y
