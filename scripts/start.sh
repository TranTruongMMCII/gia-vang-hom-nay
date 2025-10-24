#!/bin/bash


set -euo pipefail


# Load environment variables from .env if present
if [ -f ".env" ]; then
   # shellcheck disable=SC2046,SC1090
   set -a && source .env && set +a
fi


# Activate the virtual environment if it exists
if [ -d "venv" ]; then
   # shellcheck disable=SC1091
   source venv/bin/activate
fi


# Run the main Python script (forward any arguments)
python3 src/main.py "$@"

