#!/bin/bash

VID_PATH='./test'
declare -i REQ_FRAM=100
declare -i NUM_HARDCUTS=50
declare -i NUM_SOFTCUTS=50
declare -i NUM_NOCUTS=0
declare -i NUM_SOFTCUT_DURATION=1
declare -i FPS=24
SPLIT_RATIO=0.7

function generate_data
{
echo 'INITIATING MODULES'
python - <<START
import snipgen, cutmaker, splitdata
#snipgen.iterator('$VID_PATH', $FPS, $NUM_SOFTCUT_DURATION).run($REQ_FRAM)
cutmaker.runner(numhardcuts=$NUM_HARDCUTS, numgradualcuts=$NUM_SOFTCUTS, numnocuts=$NUM_NOCUTS).run(num_frames=$REQ_FRAM)
splitdata.split_data($SPLIT_RATIO).run()
START
} 


generate_data
