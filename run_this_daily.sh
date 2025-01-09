#!/bin/bash

# Set path
cd ~/Code/Personal/QOL_Score/

# Change sys argv to appropriate entry number
python3 QOL_input_extraction.py 145 | python3 QOL_score_compute.py
