#!/bin/bash

VID_PATH='/B_W films'
declare -i REQ_FRAM=50
SPLIT_RATIO=0.7

function generate_data
{
echo 'INITIATING MODULES'
python - <<START
import cutmaker, splitdata
cutmaker.iterator('$VID_PATH').run($REQ_FRAM)
splitdata.split_data($SPLIT_RATIO).run()
START
} 


generate_data
