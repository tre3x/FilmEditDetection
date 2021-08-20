# FilmEditDetection
[![Status](https://img.shields.io/badge/status-active-success.svg)]() 
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

## About
This is a CLI tool to detect cuts in films, especially old films with noisy and broken frames. This tool basically takes an input video and stores cuts in various formats - frame index of cuts alongwith type of cut in CSV format, timestamp in seconds of start and end shots in the film and MEP json format containing shots timestamps. 
This tool was produced for Google Summer Code 2021 with RedHenLabs and Media Ecology Project. 

## Getting Started


### Prerequisites
You need Python 3.X to run this tool

### Installation
For installing this tool with pretrained model, follow the steps below :
1. Clone this repository `git clone https://github.com/tre3x/FilmEditDetection.git`
2. Download the model weights from [here](http://google.com)
3. Install `requirements.txt` file by `pip install requirements.txt`

For installing this tool with you own trained model, follow the steps below :
1. Clone this repository `git clone https://github.com/tre3x/FilmEditDetection.git`
2. Go to `data/synthetic_data` and run `run.sh` with neccessary parameters. All parameters can be tweaked from the shell file. This step will download videos from the TRECVID IACC.3 dataset, and process them into small snippets of N frames containing cuts or no-cuts.
3. Go to `data/MEP_data` and run `run.sh` with neccessary parameters. This step is only valid for Media Ecology Project's video data, and it is designed to produce small snippets with cuts from the very specific annotation format it uses.
4. Install `requirements.txt` file by `pip install requirements.txt`

Now we have the data that can be used for training and testing.
#### Training
Now we have the data, we can train the model by running `data/train.sh`. The training parameters can be tweaked in the particular file. For training the model :
1. Run `cd model`
2. Tweak the training parameters in the file `train.sh`
3. Run `./train.sh`

## Usage

To run the tool on local machine, follow the steps in the **Installation** section.
After setting up the environment, Run :
```bash
python main.py --vidpath <path/to/video> --modpath <path/to/model> --operation <result_output_format>
```
- `<path/to/video>` - Path of target video path
- `<modpath>` - Path of the trained model trained/downloaded previously
- `<result_output_format>` - Output format of the result. Available formats : `cuts` - CSV file containing frame index of cuts, `shots` - CSV file containing timestamps of shots, `mepformat` - JSON format containing timestamps of shots in Media Ecology Project annotation format, `read-only` - to get timestamps of cut frames at the terminal, without writing the data to any file.

  To get help about the syntax format : `python main.py --help`
  
## Singularity Usage
To access Singularity image of this tool in the CWRU HPC environment :
1. Connect to CWRU VPN
2. ssh into HPC
```bash
ssh abc123@rider.case.edu
```
3. Navigate to this project folder directory
```bash
cd /mnt/rds/redhen/gallina/home/sxg1139/GSOC_SINGULARITY
```
4. Request a GPU node for computation
```bash
srun -p gpu -C gpu2080 gpu=gres:1 --pty bash
```
5. Load Singularity into HPC environment
```bash
module load singularity/3.7.1
```
6. Run the image
```bash
singularity run -B <path/to/video> -B <path/to/model> filmedit.img --vidpath <path/to/video> --modpath <path/to/model> 
```
- `<path/to/video>` denotes the absolute input video path
- `<path/to/model>` denotes the absolute path to trained model. If empty, the tool will tun on pre trained model.

