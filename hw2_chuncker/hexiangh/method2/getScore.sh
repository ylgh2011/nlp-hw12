#!/bin/bash

python spec_avg_perc.py -m model.ignore
[ $? -ne 0 ] && exit 1
python perc.py -m model.ignore > output.ignore
[ $? -ne 0 ] && exit 1
python score-chunks.py -t output.ignore

