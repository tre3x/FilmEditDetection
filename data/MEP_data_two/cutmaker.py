import os
import cv2
import random
import numpy as np
import glob


class cut():
    def __init__(self, vidPath1, vidPath2, outpath, duration):
        self.shot1 = cv2.VideoCapture(vidPath1)
        self.shot2 = cv2.VideoCapture(vidPath2)
        self.length1 = int(self.shot1.get(cv2.CAP_PROP_FRAME_COUNT))
        self.length2 = int(self.shot2.get(cv2.CAP_PROP_FRAME_COUNT))
        self.height = int(self.shot1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.shot1.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = int(self.shot1.get(cv2.CAP_PROP_FPS))
        self.duration = duration
        self.out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (self.width, self.height))

    def write_video(self, shotobj):
        while True:
            ret, frame = shotobj.read()
            if not ret:
                break
            else:
                self.out.write(frame)
    
    def create_transition(self, alpha):
        count = 0
        while(count<int(self.duration*self.fps)):
            self.shot1.set(cv2.CAP_PROP_POS_FRAMES, (self.length1-int(self.duration*self.fps))+count)
            res1, frame1 = self.shot1.read()
            self.shot2.set(cv2.CAP_PROP_POS_FRAMES, count)
            res2, frame2 = self.shot2.read()
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
            frame = np.add((frame1*alpha), (frame2*(1-alpha))).astype(np.uint8) #Intermediate frame = F1*α + F2*(1-α), α ∈ [0, 1] in soft cut and α = {1,0} in hard cuts.
            alpha = alpha - (1/(self.fps * 1))
            count = count + 1
            frame = self.add_noise(frame)
            self.out.write(frame)

    def make(self,alpha):
        self.write_video(self.shot1)
        self.create_transition(alpha)
        self.write_video(self.shot2)
        self.out.release()     

class runner():
    def __init__(self, snippath, numcuts):
        here = os.path.dirname(os.path.abspath(__file__))
        self.snippath = snippath
        self.numcuts = numcuts
        self.outdirpath = os.path.join(here, "cuts")
    
    def checkdir(self):
        if not os.path.isdir(self.outdirpath):
            os.mkdir(self.outdirpath)

    def getFiles(self):
        files = []
        for x in os.walk(self.snippath):
            for y in glob.glob(os.path.join(x[0], '*.avi')):
                files.append(y)
        return files

    def run(self, duration, alpha):
        self.checkdir()
        files = self.getFiles()
        if(self.numcuts>0):
            print("Generating gradual cuts...") 
            for i in range(self.numcuts):
                cuts = random.sample(range(0, len(files)-1), 2)
                outpath = os.path.join(self.outdirpath, "{}.avi".format(i))
                cut(files[0], files[1], outpath, duration).make(alpha)
        
if __name__=='__main__':
    runner('/home/at02400@ens.ad.etsmtl.ca/FilmEditDetection/data/MEP_data_two/snips', 100).run(0.1, 0.1)