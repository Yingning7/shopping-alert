#!/bin/bash

CONDA_ENV_NAME="shopping-alert"
CONDA_REQUIREMENT_FILE="conda-requirements.txt"
POSTGRES_IMG_NAME="postgres"
POSTGRES_IMG_TAG="15"
POSTGRES_CONTAINER_NAME="shopping-alert-pg-db"
POSTGERS_CONTAINER_VOLUME="/home/${USER}/Documents/shopping-alert-data"
POSTGRES_CONTAINER_PORT="5432"
POSTGRES_DB="shopping-alert-pg-db"
POSTGRES_USER="admin"
POSTGRES_PASSWORD="admin"
