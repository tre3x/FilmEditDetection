import os
import glob
from shutil import copy
import random

class split_data():
    def __init__(self, split_ratio):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.ratio = split_ratio
        self.softcutpath_src = os.path.join(self.here, "trim_video", "softcut")
        self.nocutpath_src = os.path.join(self.here, "trim_video", "nocut")

    def check_dir(self):
        base_path = os.path.join(self.here, "finaldata")
        train_path = os.path.join(base_path, "train")
        test_path = os.path.join(base_path, "test")
        self.train_nocut_path = os.path.join(train_path, "no_cut")
        self.train_softcut_path = os.path.join(train_path, "soft_cut")
        self.test_nocut_path = os.path.join(test_path, "no_cut")
        self.test_softcut_path = os.path.join(test_path, "soft_cut")

        dir_path = [base_path, train_path, test_path, self.train_nocut_path, self.train_softcut_path, self.test_nocut_path, self.test_softcut_path]

        for path in dir_path:
            if not os.path.isdir(path):
                os.mkdir(path)

    def vidpaths(self, vidpath):
        cutpaths = []
        for x in os.walk(vidpath):
            for y in glob.glob(os.path.join(x[0], '*.avi')):
                cutpaths.append(y)

        return cutpaths

    def copy_softcuts(self, softcutpath_src, train_softcut_path, test_softcut_path):
        softcuts = self.vidpaths(softcutpath_src)
        random.shuffle(softcuts)

        for softcut in softcuts[0:int(self.ratio*len(softcuts))]:
            copy(softcut, train_softcut_path)

        for softcut in softcuts[int(self.ratio*len(softcuts)):]:
            copy(softcut, test_softcut_path)

    def copy_nocuts(self, nocutpath_src, train_nocut_path, test_nocut_path):
        nocuts = self.vidpaths(nocutpath_src)
        random.shuffle(nocuts)

        for nocut in nocuts[0:int(self.ratio*len(nocuts))]:
            copy(nocut, train_nocut_path)

        for nocut in nocuts[int(self.ratio*len(nocuts)):]:
            copy(nocut, test_nocut_path)

    def run(self):
        self.check_dir()
        print("Splitting softcut video datas...")
        self.copy_softcuts(self.softcutpath_src, self.train_softcut_path, self.test_softcut_path)   
        print("Splitting nocut video datas...") 
        self.copy_nocuts(self.nocutpath_src, self.train_nocut_path, self.test_nocut_path)  
    

if __name__ == '__main__':
    split_data(0.5).run()
