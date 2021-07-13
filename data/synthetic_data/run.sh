#!/bin/bash

XML_PATH='iacc.3.collection.xml'
MSB_PATH='msb'
declare -i VID_DOWNLOAD=0
declare -i NUM_SHOTS=1
declare -i REQ_FPS=24
declare -i NUM_HARDCUTS=10
declare -i NUM_SOFTCUTS=10
declare -i SOFTCUT_DURN=1
declare -i REQ_FRAM=50
NOISE=True
SOFTCUT_CSVPATH='/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/results/softcuts/timestamps.csv'
HARDCUT_CSVPATH='/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/results/hardcuts/timestamps.csv'
SPLIT_RATIO=0.8

function generate_data
{
echo 'INITIATING MODULES'
python - <<START
import viddownload, shotmaker, cutgenerator, trimmervideo, finaldata
viddownload.downloader("$XML_PATH", $VID_DOWNLOAD)
shotmaker.shotgenerator("$MSB_PATH", $REQ_FRAM).iterator($NUM_SHOTS, $NOISE)
cutgenerator.runner($NUM_HARDCUTS, $NUM_SOFTCUTS, $REQ_FPS, $SOFTCUT_DURN)
trimmervideo.reader($REQ_FPS, $REQ_FRAM, softcut=True).run("$SOFTCUT_CSVPATH")
trimmervideo.reader($REQ_FPS, $REQ_FRAM, hardcut=True).run("$HARDCUT_CSVPATH")
trimmervideo.reader($REQ_FPS, $REQ_FRAM, nocut=True).run("$SOFTCUT_CSVPATH")
finaldata.split_data($SPLIT_RATIO).run()
START
} 


generate_data
