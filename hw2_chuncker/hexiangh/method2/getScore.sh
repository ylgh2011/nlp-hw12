#!/bin/bash

python Voting_MDR.py -m model.ignore
[ $? -ne 0 ] && exit 1
python perc.py -m model.ignore > output.ignore
[ $? -ne 0 ] && exit 1
python score-chunks.py -t output.ignore
