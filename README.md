# FilmEditDetection
[![Status](https://img.shields.io/badge/status-active-success.svg)]() 
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

## About
This is a CLI tool to detect cuts in films, especially old films with noisy and broken frames. This tool basically takes an input video and stores cuts in various formats - frame index of cuts alongwith type of cut in CSV format, timestamp in seconds of start and end shots in the film, MEP json format containing shots timestamps, and a format which is supported by cinemetrics for further analysis. 
This tool was produced for Google Summer Code 2021 with RedHenLabs and Media Ecology Project. 

Detailed working of this tool is included in the [final submission blog](https://gsocblog-tre3x.netlify.app/final-project.html).

## Getting Started


### Prerequisites
You need Python 3.x and Conda package manager to run this tool

### Installation
For installing this tool with pretrained model, follow the steps below :
1. Clone this repository `git clone https://github.com/tre3x/FilmEditDetection.git`
2. Install the neccessary dependencies by executing `conda env create -f environment.yml`

### Dataset Description
Two datasets were used in training the validation/softcut-detection module.
1. The first dataset used is TRECVID IACC.3 dataset. This video dataset comprises of annotated videos which are further used to create synthetically generated snippets containing hard-cut, soft-cut or no-cut. One way to generate the training data is defined as follows: Go to `data/synthetic_data` and run `run.sh` with neccessary parameters. All parameters can be tweaked from the shell file. This step will download videos from the TRECVID IACC.3 dataset, and process them into small snippets of N frames containing cuts or no-cuts.
2. The second dataset used is Media Ecology Project's B&W video data, which contains fully annotated films, which has great resemblence to the kind of data we are actually dealing with in this work. One way to generate the training data is defined as follows: Go to `data/MEP_data` and run `run.sh` with neccessary parameters. This step is only valid for Media Ecology Project's video data, and it is designed to produce small snippets with cuts from the very specific annotation format it uses.

Now we have the data that can be used for training and testing.


### Pre-Trained Model
One pre-trained model of specific configuration is available, which can be found [here](https://drive.google.com/file/d/1KdyW31aCh6iD1Ot0RJK-N14-4A4NHNiD/view?usp=sharing).

#### Training
Now we have the data, we can train the model by running `data/train.sh`. The training parameters can be tweaked in the particular file. For training the model :
1. Run `cd model`
2. Tweak the training parameters in the file `train.sh`
3. Run `./train.sh`

## Usage

To run the tool on local machine, follow the steps in the **Installation** section.
After setting up the environment, Run :
```bash
python main.py --vidpath <path/to/video> --modpath <path/to/model> --operation <result_output_format> --config <path/to/config>
```
- `<path/to/video>` - Path of target video path.
- `<modpath>` - Path of the model trained/downloaded previously. Default path : `.\trained-models\cutdetection-model`
- `<result_output_format>` - Output format of the result. Available formats : `cuts` - CSV file containing frame index of cuts, `shots` - CSV file containing timestamps of shots, `mepformat` - JSON format containing timestamps of shots in Media Ecology Project annotation format, `cinemetrics` - a '.cns' formatted file which is supported for uploading to [cinemetrics](http://www.cinemetrics.lv/), `read-only` - to get timestamps of cut frames at the terminal, without writing the data to any file. Default mode : `read-only`
- `<path/to/config>` - Path to network configuration file. This file (in json format) should contain all information about the networks used in the tool. Few default congigs are stored in the `config` folder. Default path : `.\configs\vgg16.json`

  To get help about the syntax format : `python main.py --help`

## MEP Dataset
The Media Ecology Project's black and white manually annotated video dataset highly resembles the kind of old archival films whose shot boundaries are hard to predict by other computer-based cut detection tools. Hence, the annotated video dataset is very helpful in training the deep learning models used in this tool and making the prediction of shot boundaries in other archival films. The annotated dataset is made possible with the efforts of [Mark J. Williams](https://faculty-directory.dartmouth.edu/mark-j-williams), [John P. Bell](https://itc.dartmouth.edu/people/john-p-bell), and students from Dartmouth College and University of Chicago:
- Yangqiao Lu, University of Chicago
- Emily Hester, Dartmouth College
- Elijah Czysz, Dartmouth College
- Noah Hensley, Dartmouth College
- Ileana Sung, Dartmouth College
- Adithi Jayaraman, Dartmouth College
- Momina Naveed, Dartmouth College
- Maria Graziano, Dartmouth College
- Kevin Chen, Dartmouth College
- Frandy Rodriguez, Dartmouth College
  
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

## Future Work
- Additional features can be added to the tool which provides helpful insights into the film metrics.
- There are few cases in which the tool fails to classify cuts, like in case of Jump cuts. In the future some other variant of the model
can be used to classify the cuts which the current model fails to classify.
- Some films have low contrast with high noise, in which it becomes difficult to classify cuts. Some preprocessing on training data to acheive the same
and let the model learn those features.
- The command line interface can currently handle one output operation at a time. It can be modified 
 to allow the user to generate outputs of multiple format at a time.
