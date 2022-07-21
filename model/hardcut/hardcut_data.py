import os
import cv2
import argparse

DIR_NAME = {'hardcut': 'hard-cut', 'nocut' : 'no_cut'}

class hardcut_data():
    def __init__(self, train_path, test_path):
        here = os.path.dirname(os.path.abspath(__file__))
        self.train_path = train_path
        self.test_path = test_path
        self.outdir = os.path.join(here, "data")
        self.traindir = os.path.join(self.outdir, "train")
        self.testdir = os.path.join(self.outdir, "test")
        self.nocuttraindir = os.path.join(self.traindir, DIR_NAME['nocut'])
        self.hardcuttraindir = os.path.join(self.traindir, DIR_NAME['hardcut'])
        self.nocuttestdir = os.path.join(self.testdir, DIR_NAME['nocut'])
        self.hardcuttestdir = os.path.join(self.testdir, DIR_NAME['hardcut'])
        self.validate_dir()

    def validate_dir(self):
        assert os.path.isdir(os.path.join(self.train_path, DIR_NAME['hardcut'])), 'Please make sure {} directory is present in {}!!'.format(DIR_NAME['hardcut'], self.train_path)
        assert os.path.isdir(os.path.join(self.train_path, DIR_NAME['nocut'])), 'Please make sure {} directory is present in {}!!'.format(DIR_NAME['nocut'], self.train_path)
        assert os.path.isdir(os.path.join(self.test_path, DIR_NAME['hardcut'])), 'Please make sure {} directory is present in {}!!'.format(DIR_NAME['hardcut'], self.test_path)
        assert os.path.isdir(os.path.join(self.test_path, DIR_NAME['nocut'])), 'Please make sure {} directory is present in {}!!'.format(DIR_NAME['nocut'], self.test_path)
        self.check_dir(self.outdir)
        self.check_dir(self.traindir)
        self.check_dir(self.testdir)
        self.check_dir(self.nocuttraindir)
        self.check_dir(self.hardcuttraindir)
        self.check_dir(self.nocuttestdir)
        self.check_dir(self.hardcuttestdir)

    def check_dir(self, dirpath):
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)

    def store_frame(self, cap, index, dirpath, name):
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = cap.read()
        cv2.imwrite(os.path.join(dirpath, name), frame)

    def process_cut(self, path, dirpath):
        cap = cv2.VideoCapture(path)
        length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.store_frame(cap, (length//2)-1, dirpath, "1.png")
        self.store_frame(cap, (length//2)+1, dirpath, "2.png")

    def get_label(self, dirpath):
        if dirpath.split('/')[-2] == DIR_NAME['hardcut'] : label = [1, 0]
        else: label = [0, 1]
        return label

    def iterate_and_process(self, hardcutspath, nocutspath, isTrain):
        paths = []
        for subdir, dirs, files in os.walk(hardcutspath):
            for file in files:
                filepath = os.path.join(subdir, file)
                if filepath.endswith(".avi") or filepath.endswith(".mp4"):
                    dirname = '.'.join(file.split('.')[:-1])
                    if isTrain: dirpath = os.path.join(self.hardcuttraindir, dirname)
                    else: dirpath = os.path.join(self.hardcuttestdir, dirname)
                    self.check_dir(dirpath)
                    self.process_cut(filepath, dirpath)
                    label = self.get_label(dirpath)
                    paths.append([dirpath, label])


        for subdir, dirs, files in os.walk(nocutspath):
            for file in files:
                filepath = os.path.join(subdir, file)
                if filepath.endswith(".avi") or filepath.endswith(".mp4"):
                    dirname = '.'.join(file.split('.')[:-1])
                    if isTrain: dirpath = os.path.join(self.nocuttraindir, dirname)
                    else: dirpath = os.path.join(self.nocuttestdir, dirname)
                    self.check_dir(dirpath)
                    self.process_cut(filepath, dirpath)
                    label = self.get_label(dirpath)
                    paths.append([dirpath, label])
        return paths

    def load_traindata(self):
        hardcutspath = os.path.join(self.train_path, DIR_NAME['hardcut'])
        nocutspath = os.path.join(self.train_path, DIR_NAME['nocut'])
        trainpaths = self.iterate_and_process(hardcutspath, nocutspath, isTrain=True)
        return trainpaths

    def load_testdata(self):
        hardcutspath = os.path.join(self.test_path, DIR_NAME['hardcut'])
        nocutspath = os.path.join(self.test_path, DIR_NAME['nocut'])
        testpaths = self.iterate_and_process(hardcutspath, nocutspath, isTrain=False)
        return testpaths

    def run(self):
        trainpaths = self.load_traindata()
        testpaths = self.load_testdata()
        return trainpaths, testpaths


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='HardCut Data Generation Tool')

    parser.add_argument('--trainpath', type=str, default='', help='What is the training directory path?')
    parser.add_argument('--testpath', type=str, default='', help='What is the test directory path?')

    args = parser.parse_args()

    x, y = hardcut_data(args.trainpath, args.testpath).run()