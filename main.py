import os
import argparse
from run import run
from utils import load_config

def main():
    parser = argparse.ArgumentParser(description='Film Edit Detection CLI tool')

    parser.add_argument('--vidpath', type=str, default='', nargs='+', help='What is the input video path?')
    parser.add_argument('--modpath', type=str, default='', nargs='+', help='What is the path of trained 3DCNN model')
    parser.add_argument('--operation', type=str, default='', help='What is the output content?(cuts, shots, mepformat)')
    parser.add_argument('--config', metavar='CONFIG_FILE', help='What is the path to configuration file?')

    args = parser.parse_args()
    vidpath = ' '.join(args.vidpath)
    modpath = ' '.join(args.modpath)
    conf = load_config(args.config)

    assert vidpath != '', "Video Path cannot be blank"

    if modpath=='':
        here = os.path.dirname(os.path.abspath(__file__))
        modpath=os.path.join(here, "trained-models", "cutdetection-model")
        if not os.path.isdir(modpath):
            print("No trained model found!!")
    if args.operation=='':
        args.operation='read-only'

    print("Configuration")
    print("----------------------------------------------------------------------")
    print("Video Path : {}".format(vidpath))
    print("Model Path : {}".format(modpath))
    print("Operation : {}".format(args.operation))
    print("Network Config path : {}".format(args.config))
    print("----------------------------------------------------------------------")

    if args.operation=='cuts':
        run(conf).run(vidpath, modpath, iscsvframe=True)
    if args.operation=='shots':
        run(conf).run(vidpath, modpath, iscsvtime=True)
    if args.operation=='mepformat':
        run(conf).run(vidpath, modpath, ismepjson=True)
    if args.operation=='read-only':
        run(conf).run(vidpath, modpath, readonly=True)


if __name__=='__main__':
    main()