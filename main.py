import os
import argparse
from run import run
from utils import load_config

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_MODEL_PATH = os.path.join(here, "trained-models", "cutdetection-model")
    DEFAULT_CONFIG_PATH = os.path.join(here, "configs", "vgg16.json")
    
    parser = argparse.ArgumentParser(description='Film Edit Detection CLI tool')

    parser.add_argument('--vidpath', required = True, help='What is the input video path?')
    parser.add_argument('--modpath', default=DEFAULT_MODEL_PATH, help='What is the path of trained 3DCNN model')
    parser.add_argument('--operation', default='read-only', help='What is the output content?(cuts, shots, mepformat)')
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH, help='What is the path to configuration file?')

    args = parser.parse_args()
    conf = load_config(args.config)

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

    if args.operation=='cuts':
        run(conf).run(args.vidpath, args.modpath, iscsvframe=True)
    if args.operation=='shots':
        run(conf).run(args.vidpath, args.modpath, iscsvtime=True)
    if args.operation=='mepformat':
        run(conf).run(args.vidpath, args.modpath, ismepjson=True)
    if args.operation=='read-only':
        run(conf).run(args.vidpath, args.modpath, readonly=True)


if __name__=='__main__':
    main()