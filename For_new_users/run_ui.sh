#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set up the environment
export PATH=/opt/anaconda3/bin:/opt/anaconda3/condabin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# Activate the conda environment
if [ -f /opt/anaconda3/bin/activate ]; then
  source /opt/anaconda3/bin/activate QOL_env >/dev/null 2>&1 || true
fi

# Run the Python script
python3 "$SCRIPT_DIR/Scripts/UI.py"
