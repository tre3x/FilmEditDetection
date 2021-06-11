#!/bin/bash

XML_PATH='iacc.3.collection.xml'
MSB_PATH='msb'
declare -i VID_DOWNLOAD=1
declare -i REQ_FPS=24
declare -i NUM_HARDCUTS=10
declare -i NUM_SOFTCUTS=10
declare -i SOFTCUT_DURN=1
declare -i REQ_FRAM=50

function generate_data
{
echo 'INITIATING MODULES'
python - <<START
import viddownload, cutgenerator, finaldata
viddownload.downloader("$XML_PATH", "$MSB_PATH", $VID_DOWNLOAD)
cutgenerator.runner($NUM_HARDCUTS, $NUM_SOFTCUTS, $REQ_FPS, $SOFTCUT_DURN)
finaldata.reader($REQ_FPS, $REQ_FRAM, False).run()
finaldata.reader($REQ_FPS, $REQ_FRAM, True).run()
START
echo 'DATA SUCCESSFULLY GENERATED'
} 


generate_data