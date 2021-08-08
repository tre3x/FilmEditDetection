#!/bin/bash

XML_PATH='iacc.3.collection.xml'
MSB_PATH='msb'
VID_DOWNLOAD=0
NUM_SHOTS=0
REQ_FPS=24
NUM_HARDCUTS=0
NUM_SOFTCUTS=00
REQ_FRAM=100
SOFTCUT_DURN=0.8
SPLIT_RATIO=0.7
NOISE=True
TRIM_SOFT=True
TRIM_HARD=False
TRIM_NOCUTS=False

function generate_data
{
echo 'INITIATING MODULES'
python - <<START
import viddownload, shotmaker, cutgenerator, trimmervideo, finaldata
viddownload.downloader("$XML_PATH", $VID_DOWNLOAD)
shotmaker.shotgenerator("$MSB_PATH", $REQ_FRAM).iterator($NUM_SHOTS, $NOISE)
cutgenerator.runner($NUM_HARDCUTS, $NUM_SOFTCUTS, $REQ_FPS, $SOFTCUT_DURN)
trimmervideo.reader($REQ_FPS, $REQ_FRAM, softcut=$TRIM_SOFT).run()
trimmervideo.reader($REQ_FPS, $REQ_FRAM, hardcut=$TRIM_HARD).run()
trimmervideo.reader($REQ_FPS, $REQ_FRAM, nocut=$TRIM_NOCUTS).run()
finaldata.split_data($SPLIT_RATIO).run()
START
} 

generate_data
