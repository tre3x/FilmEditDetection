import os
import sys
import glob
import random
from shutil import copy

class split_data():
    def __init__(self, split_ratio):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.ratio = split_ratio
        self.softcutpath_src = os.path.join(self.here, "cuts", "softcut")
        self.hardcutpath_src = os.path.join(self.here, "cuts", "hardcut")
        self.nocutpath_src = os.path.join(self.here, "cuts", "nocut")

    def check_dir(self):
        base_path = os.path.join(self.here, "finaldata")
        train_path = os.path.join(base_path, "train")
        test_path = os.path.join(base_path, "test")
        self.train_nocut_path = os.path.join(train_path, "no_cut")
        self.train_softcut_path = os.path.join(train_path, "soft_cut")
        self.train_hardcut_path = os.path.join(train_path, "hard-cut")
        self.test_nocut_path = os.path.join(test_path, "no_cut")
        self.test_softcut_path = os.path.join(test_path, "soft_cut")
        self.test_hardcut_path = os.path.join(test_path, "hard-cut")

        dir_path = [base_path, train_path, test_path, self.train_nocut_path, self.train_softcut_path, self.train_hardcut_path, self.test_nocut_path, self.test_softcut_path, self.test_hardcut_path]

        for path in dir_path:
            if not os.path.isdir(path):
                os.mkdir(path)

    def vidpaths(self, vidpath):
        cutpaths = []
        for x in os.walk(vidpath):
            for y in glob.glob(os.path.join(x[0], '*.mp4')):
                cutpaths.append(y)

        return cutpaths

    def copy_cuts(self, cutpath_src, train_cut_path, test_cut_path):
        cuts = self.vidpaths(cutpath_src)
        random.shuffle(cuts)

        for cut in cuts[0:int(self.ratio*len(cuts))]:
            copy(cut, train_cut_path)

        for cut in cuts[int(self.ratio*len(cuts)):]:
            copy(cut, test_cut_path)    


    def run(self):
        self.check_dir()
        sys.stdout.write("\rSplitting softcut video datas...")
        self.copy_cuts(self.softcutpath_src, self.train_softcut_path, self.test_softcut_path) 
        sys.stdout.write("\rSplitting hardcut video datas...")
        self.copy_cuts(self.hardcutpath_src, self.train_hardcut_path, self.test_hardcut_path)  
        sys.stdout.write("\rSplitting nocut video datas...")
        self.copy_cuts(self.nocutpath_src, self.train_nocut_path, self.test_nocut_path)  
        sys.stdout.write("\n")
    

if __name__ == '__main__':
    split_data(0.5).run()
