#!/bin/bash

# Set path
cd ~/Code/Personal/QOL_Score/

# Change sys argv to appropriate entry number
python3 All_in_one_QOL_input_extraction.py 1 | python3 All_in_one_QOL_score_compute.py
