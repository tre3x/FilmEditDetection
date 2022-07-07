import os
import cv2
import random
import numpy as np
import glob
from snipgen import iterator


class cut():
    def __init__(self, outpath, duration=None, num_frames = None, vidPath1=None, vidPath2=None, cuttype='no'):
        self.vidpath1 = vidPath1
        self.vidpath2 = vidPath2
        if self.vidpath1 is not None:
            self.shot1 = cv2.VideoCapture(self.vidpath1)
            self.length1 = int(self.shot1.get(cv2.CAP_PROP_FRAME_COUNT))   
            self.height = int(self.shot1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(self.shot1.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.fps = int(self.shot1.get(cv2.CAP_PROP_FPS))
        if self.vidpath2 is not None: 
            self.shot2 = cv2.VideoCapture(self.vidpath2)
            self.length2 = int(self.shot2.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cuttype = cuttype
        self.out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.width, self.height))
        if cuttype == 'hard': self.duration = 3/self.fps
        if cuttype == 'soft': self.duration = duration
        if cuttype == 'no': self.expand_frames(num_frames)
        

    def write_video(self, shotobj, start, end):
        shotobj.set(cv2.CAP_PROP_POS_FRAMES, start)
        count = 0
        while True:
            ret, frame = shotobj.read()
            if not ret or count == end:
                break
            else:
                self.out.write(frame.astype(np.uint8))
                count = count+1
    
    def create_transition(self, alpha=1):
        count = 0
        while(count<int(self.duration*self.fps)):
            self.shot1.set(cv2.CAP_PROP_POS_FRAMES, (self.length1-int(self.duration*self.fps))+count)
            res1, frame1 = self.shot1.read()
            self.shot2.set(cv2.CAP_PROP_POS_FRAMES, count)
            res2, frame2 = self.shot2.read()
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
            frame = np.add((frame1*alpha), (frame2*(1-alpha))).astype(np.uint8) 
            alpha = alpha - (1/(self.fps * 1))
            count = count + 1
            self.out.write(frame)

    def expand_frames(self, num_frames):
        orgvidpath = os.path.join("/".join(self.vidpath1.split('/')[:-3]), "B_W films", "{}.mp4".format(self.vidpath1.split('/')[-2]))
        anchor = int(self.vidpath1.split('/')[-1].split('.')[0])  #NAME OF FILM SNIPPETS IN THE SNIP FOLDER, CORRESPONDS TO ANCHOR FRAMES
        cap = cv2.VideoCapture(orgvidpath)
        for fr in range(anchor-num_frames//2, anchor+num_frames//2):
            cap.set(cv2.CAP_PROP_POS_FRAMES, fr)
            ret, frame = cap.read()
            if not ret:
                break
            else:
                self.out.write(frame.astype(np.uint8))

    def make(self):
        try:
            self.write_video(self.shot1, 0, self.length1-int(self.duration*self.fps)-1)
            self.create_transition()
            self.write_video(self.shot2, int(self.duration*self.fps), self.length2)
        except:
            pass
        self.out.release()     

class runner():
    def __init__(self, numhardcuts=0, numgradualcuts=0, numnocuts=0):
        here = os.path.dirname(os.path.abspath(__file__))
        self.snippath = os.path.join("snips")
        self.numgradualcuts = numgradualcuts
        self.numhardcuts = numhardcuts
        self.numnocuts = numnocuts
        self.outdirpath = os.path.join(here, "cuts")
    
    def checkdir(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)

    def getFiles(self):
        files = []
        for x in os.walk(self.snippath):
            for y in glob.glob(os.path.join(x[0], '*.avi')):
                files.append(y)
        return files

    def run(self, duration=1, num_frames=100):
        self.checkdir(self.outdirpath)
        files = self.getFiles()
        

        if(self.numhardcuts > 0):
            print("Generating hard cut snippets...")
            hardcutdir = os.path.join(self.outdirpath, "hardcuts")
            self.checkdir(hardcutdir)
            for i in range(self.numhardcuts):
                cuts = random.sample(range(0, len(files)-1), 2)
                outpath = os.path.join(hardcutdir, "{}.mp4".format(i))
                cut(outpath, duration = duration, vidPath1 = files[cuts[0]], vidPath2 = files[cuts[1]], cuttype = "hard").make()

        if(self.numgradualcuts>0):
            print("Generating gradual cut snippets...") 
            softcutdir = os.path.join(self.outdirpath, "softcuts")
            self.checkdir(softcutdir)
            for i in range(self.numgradualcuts):
                cuts = random.sample(range(0, len(files)-1), 2)
                outpath = os.path.join(softcutdir, "{}.mp4".format(i))
                cut(outpath, duration = duration, vidPath1 = files[cuts[0]], vidPath2 = files[cuts[1]], cuttype = "soft").make()

        if(self.numnocuts>0):
            print("Generating no cut snippets...") 
            nocutdir = os.path.join(self.outdirpath, "nocuts")
            self.checkdir(nocutdir)
            for i in range(self.numnocuts):
                cuts = random.sample(range(0, len(files)-1), 1)
                outpath = os.path.join(nocutdir, "{}.mp4".format(i))
                cut(outpath, num_frames = 100, vidPath1 = files[cuts[0]], cuttype = "no")