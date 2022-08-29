import os
import argparse
from . import run
from . import load_config

def run_tool(vidpath, modpath, operation, outdir, config, cinemetrics_submit, yname, mtitle, myear, email):
    here = os.path.dirname(os.path.abspath(__file__))
    conf = load_config(config)
    if operation=='cuts':
        if outdir=='':
            outdir = os.path.join(here, "csv_cuts")
        run(conf).run(vidpath, modpath, outdir, iscsvframe=True)
    if operation=='shots':
        if outdir=='':
            outdir = os.path.join(here, "csv_shots")
        run(conf).run(vidpath, modpath, outdir, iscsvtime=True)
    if operation=='mepformat':
        if outdir=='':
            outdir = os.path.join(here, "json_mep")
        run(conf).run(vidpath, modpath, outdir, ismepjson=True)
    if operation=='cinemetrics':
        if outdir=='':
            outdir = os.path.join(here, "cinemetrics")
        if cinemetrics_submit==True:
            cine_details = {'yname':yname, 'mtitle':mtitle, 'myear':myear,'email':email}
            run(conf).run(vidpath, modpath, outdir, iscinemetrics=True, submit=True, cine_details=cine_details)
        else:
            run(conf).run(vidpath, modpath, outdir, iscinemetrics=True)
    if operation=='read-only':
        run(conf).run(vidpath, modpath, readonly=True)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_MODEL_PATH = os.path.join(here, "trained-models", "cutdetection-model")
    DEFAULT_CONFIG_PATH = os.path.join(here, "configs", "vgg16.json")
    
    parser = argparse.ArgumentParser(description='Film Edit Detection CLI tool')

    parser.add_argument('--vidpath', required = True, help='What is the input video path?')
    parser.add_argument('--modpath', default=DEFAULT_MODEL_PATH, help='What is the path of trained 3DCNN model')
    parser.add_argument('--operation', default='read-only', help='What is the output content?(cuts, shots, mepformat, cinemetrics)')
    parser.add_argument('--outdir', default='', help='What is the directory of the saved output file?')
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH, help='What is the path to configuration file?')
    parser.add_argument('--cinemetrics_submit', default=False, action="store_true", help='Whether you want to upload the cut detection result to cinemetrics server?')
    parser.add_argument('--yname', default='', help='What is the submitter name?')
    parser.add_argument('--mtitle', default='', help='What is the movie title')
    parser.add_argument('--myear', default='', help='What is the movie year?')
    parser.add_argument('--email', default='', help='What is the submitter email?')

    args = parser.parse_args()

    assert os.path.isfile(args.vidpath), "No video file found!!"
    assert os.path.isdir(args.modpath), "No trained model found!!"
    assert os.path.isfile(args.config), "No network configuration file found!!"

    print("Configuration")
    print("----------------------------------------------------------------------")
    print("Video Path : {}".format(args.vidpath))
    print("Model Path : {}".format(args.modpath))
    print("Operation : {}".format(args.operation))
    print("Network Config path : {}".format(args.config))
    print("----------------------------------------------------------------------")
    run_tool(args.vidpath, args.modpath, args.operation, args.outdir, args.config, args.cinemetrics_submit, args.yname, args.mtitle, args.myear, args.email)

if __name__=='__main__':
    main()