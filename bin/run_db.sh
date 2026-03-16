#!/bin/bash

# SYNOPSIS
#     Script to easily manage local PostgreSQL docker container.
# DESCRIPTION
#     Available commands: start, stop, resume, terminate, bounce
#     Will use variables from db.env if present.

COMMAND=$1

if [[ ! "$COMMAND" =~ ^(start|stop|resume|terminate|bounce)$ ]]; then
    echo "Usage: $0 {start|stop|resume|terminate|bounce}"
    exit 1
fi

# Load environment from db.env located in the same directory as this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_FILE="${SCRIPT_DIR}/db.env"

if [ -f "$ENV_FILE" ]; then
    echo -e "\e[36mLoading environment variables from $ENV_FILE\e[0m"
    set -a
    source "$ENV_FILE"
    set +a
else
    echo -e "\e[33mEnvironment file not found at $ENV_FILE. Using existing environment variables or defaults.\e[0m"
fi

# Configuration
IMAGE_NAME="${IMAGE_NAME:-postgres:14}"
CONTAINER_NAME="${CONTAINER_NAME:-shopping-alert-db}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
PORT="${PORT:-5432}"

# Check container state
STATUS=$(sudo docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || true)

if [ -n "$STATUS" ]; then
    EXISTS=true
else
    EXISTS=false
fi

if [ "$STATUS" = "running" ]; then
    IS_RUNNING=true
else
    IS_RUNNING=false
fi

if [[ "$STATUS" == "exited" || "$STATUS" == "created" || "$STATUS" == "dead" ]]; then
    IS_STOPPED=true
else
    IS_STOPPED=false
fi

start_new_db() {
    echo -e "\e[32mStarting a new PostgreSQL ($IMAGE_NAME) container '$CONTAINER_NAME'...\e[0m"
    echo -e "\e[90mUser: $POSTGRES_USER | DB: $POSTGRES_DB | Port: $PORT\e[0m"
    
    sudo docker run -d \
        --name "$CONTAINER_NAME" \
        -p "${PORT}:5432" \
        -e "POSTGRES_USER=$POSTGRES_USER" \
        -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" \
        -e "POSTGRES_DB=$POSTGRES_DB" \
        "$IMAGE_NAME" > /dev/null
        
    echo -e "\e[32mDatabase started successfully!\e[0m"
}

terminate_db() {
    echo -e "\e[33mTerminating container '$CONTAINER_NAME'...\e[0m"
    if [ "$IS_RUNNING" = true ]; then
        sudo docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
    sudo docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    echo -e "\e[32mDatabase terminated and removed.\e[0m"
}

case $COMMAND in
    start)
        if [ "$IS_RUNNING" = true ]; then
            echo -e "\e[36mContainer '$CONTAINER_NAME' is already running. Ignoring.\e[0m"
        elif [ "$IS_STOPPED" = true ]; then
            echo -e "\e[36mContainer '$CONTAINER_NAME' is currently stopped. Ignoring.\e[0m"
        else
            start_new_db
        fi
        ;;
    stop)
        if [ "$IS_RUNNING" = true ]; then
            echo -e "\e[33mStopping running container '$CONTAINER_NAME'...\e[0m"
            sudo docker stop "$CONTAINER_NAME" > /dev/null 2>&1
            echo -e "\e[32mDatabase stopped.\e[0m"
        elif [ "$IS_STOPPED" = true ]; then
            echo -e "\e[36mContainer '$CONTAINER_NAME' is already stopped. Ignoring.\e[0m"
        else
            echo -e "\e[36mNo container to stop. Ignoring.\e[0m"
        fi
        ;;
    resume)
        if [ "$IS_STOPPED" = true ]; then
            echo -e "\e[32mResuming stopped container '$CONTAINER_NAME'...\e[0m"
            sudo docker start "$CONTAINER_NAME" > /dev/null 2>&1
            echo -e "\e[32mDatabase resumed.\e[0m"
        elif [ "$IS_RUNNING" = true ]; then
            echo -e "\e[36mContainer '$CONTAINER_NAME' is already running. Ignoring.\e[0m"
        else
            echo -e "\e[36mNo stopped container to resume. Ignoring.\e[0m"
        fi
        ;;
    terminate)
        if [ "$EXISTS" = true ]; then
            terminate_db
        else
            echo -e "\e[36mNo container to terminate. Ignoring.\e[0m"
        fi
        ;;
    bounce)
        if [ "$EXISTS" = true ]; then
            echo -e "\e[33mContainer '$CONTAINER_NAME' exists. Terminating first...\e[0m"
            terminate_db
        fi
        start_new_db
        ;;
esac
