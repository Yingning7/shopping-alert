#!/bin/bash

source ./bin/vars.sh

conda create -n $CONDA_ENV_NAME --file "./bin/$CONDA_REQUIREMENT_FILE" -y
sudo docker pull "${POSTGRES_IMG_NAME}:${POSTGRES_IMG_TAG}"
mkdir $POSTGERS_CONTAINER_VOLUME
