#!/bin/bash

# SYNOPSIS
#     Initial project setup script for Linux/macOS.
# DESCRIPTION
#     1. Checks if 'uv' (Python package manager) is installed, and prompts the user to install it if not.
#     2. Runs 'uv sync' to install project dependencies.
#     3. Runs 'uv run playwright install' to download Playwright browsers.

set -e

echo -e "\e[36mStarting project setup...\e[0m"

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "\e[31mError: 'uv' is not installed.\e[0m"
    echo -e "\e[33mPlease install uv first by running:\e[0m"
    echo -e "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo -e "\e[33mThen restart your terminal or source your profile and run this script again.\e[0m"
    exit 1
else
    echo -e "\e[32muv is already installed.\e[0m"
fi

# 2. uv sync
echo -e "\n\e[36mRunning 'uv sync'...\e[0m"
if ! uv sync; then
    echo -e "\e[31mError: uv sync encountered an error.\e[0m"
    exit 1
fi

# 3. playwright install
echo -e "\n\e[36mRunning 'uv run playwright install'...\e[0m"
if ! uv run playwright install; then
    echo -e "\e[31mError: playwright install encountered an error.\e[0m"
    exit 1
fi

echo -e "\n\e[36mInstalling playwright system dependencies (requires sudo)...\e[0m"
if ! uv run playwright install-deps; then
    echo -e "\e[31mError: playwright install-deps encountered an error.\e[0m"
    exit 1
fi

echo -e "\n\e[32mSetup completed successfully!\e[0m"
