#!/bin/bash

for i in {0..19}
do
	python perc.py -m model_$i | python score-chunks.py
done

