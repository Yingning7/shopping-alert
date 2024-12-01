#!/bin/bash

source ./bin/vars.sh

case $1 in
  start)
    sudo docker run --name $POSTGRES_CONTAINER_NAME -p "${POSTGRES_CONTAINER_PORT}:5432" -e POSTGRES_DB=$POSTGRES_DB -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -v "${POSTGERS_CONTAINER_VOLUME}:/var/lib/postgresql/data" -d "${POSTGRES_IMG_NAME}:${POSTGRES_IMG_TAG}"
    ;;
  terminate)
    sudo docker stop $POSTGRES_CONTAINER_NAME
    sudo docker rm $POSTGRES_CONTAINER_NAME
    ;;
esac
