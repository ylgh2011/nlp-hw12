#!/bin/bash

python avg_perc.py -m model_$1 -e $1
[ $? -ne 0 ] && exit 1
python perc.py -m model_$1 > output_$1
[ $? -ne 0 ] && exit 1
python score-chunks.py -t output_$1

