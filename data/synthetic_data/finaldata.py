import os
import cv2
import csv
import random
import numpy as np

class softcutdatamaker():
    '''
    This class generates video snippets with no cut in them, i.e. pure shots, given
    INPUT : path, initframe, finframe, fps, framenum
    path - path of the video file,
    initframe - starting frame of cut in the video,
    finframe - end frame of cut in the video,
    fps - required frames per seconds of the video snippet,
    framenum - number of frames to be present in the snippet
    '''
    def __init__(self, path, initframe, finframe, fps, framenum):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.path = path
        self.initframe = int(initframe)
        self.finframe = int(finframe)
        self.fps = fps
        self.framenum = framenum
        self.check_dir()

    def check_dir(self):
        '''
        Checks if the directory where videos snippets with soft cuts are to be stored, 
        are already present
        '''
        finaldatapath = os.path.join(self.here, "finaldata")
        if not os.path.isdir(finaldatapath):
            os.mkdir(finaldatapath)
        softcutpath = os.path.join(finaldatapath, "softcut")
        if not os.path.isdir(softcutpath):
            os.mkdir(softcutpath)
        
    def trim_video(self):
        '''
        Trims the parent video according to a reference frame to produce shorter video snippet
        of required frames, containg a soft cut in between.
        '''
        cap = cv2.VideoCapture(self.path)
        outpath = os.path.join(self.here, "finaldata", "softcut", self.path.split("/")[-1])
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))

        referenceframe = random.randint(self.initframe, self.finframe)
        startframe = referenceframe - self.framenum//2
        framecount = startframe

        while framecount <= startframe+self.framenum:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(framecount))
            res, frame = cap.read()
            out.write(frame)
            framecount = framecount + 1
        out.release()

    def run(self):
        self.trim_video()

class nocutdatamaker():
    '''
    This class generates video snippets with soft cut in them, given
    INPUT : path, initframe, finframe, fps, framenum
    path - path of the video file,
    initframe - starting frame of cut in the video,
    finframe - end frame of cut in the video,
    fps - required frames per seconds of the video snippet,
    framenum - number of frames to be present in the snippet
    '''
    def __init__(self, path, initframe, finframe, fps, framenum):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.path = path
        self.initframe = int(initframe)
        self.finframe = int(finframe)
        self.fps = fps
        self.framenum = framenum
        self.cap = cv2.VideoCapture(self.path)
        self.check_dir()

    def check_dir(self):
        '''
        Checks if the directory where videos snippets with soft cuts are to be stored, 
        are already present
        '''
        finaldatapath = os.path.join(self.here, "finaldata")
        if not os.path.isdir(finaldatapath):
            os.mkdir(finaldatapath)
        nocutpath = os.path.join(finaldatapath, "nocut")
        if not os.path.isdir(nocutpath):
             os.mkdir(nocutpath)

    def get_referenceframe(self):
        '''
        Get reference frame about which trimming of the parent video is going to take place,
        to produce shorter video snippet with no cut in between.
        '''
        while True:
            frame = random.randint(0, self.length-1)
            if self.initframe - frame > self.framenum:
                return frame
            if (frame > self.finframe) and (self.length - frame > self.framenum):
                return frame

    def trim_video(self):
        '''
        Trims the parent video according to a reference frame to produce shorter video snippet
        of required frames, containg no cut in between.
        '''
        outpath = os.path.join(self.here, "finaldata", "nocut", self.path.split("/")[-1])
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))

        referenceframe = self.get_referenceframe()
        framecount = referenceframe
        while framecount <= referenceframe+self.framenum:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(framecount))
            res, frame = self.cap.read()
            self.out.write(frame)
            framecount = framecount + 1
        self.out.release()

    def run(self):
        ################
        #DRIVER FUNCTION
        ################
        self.trim_video()

class reader():
    '''
    This class takes CSV timestamps generated by cutgenerator module, and generates snippets of given frame
    of soft cuts or not cut. This data is required for training the 3D CNNs. Results will be stored in
    'finaldata/nocut' or 'finaldata/softcut'.
    INPUT : csvpath, fps, framenum, nocut
    csvpath - path of the previously generated csv file containing timestamps,
    fps - required frames per second of the snippet video,
    framenum - number of frames to be present in the snippet,
    nocut - a boolean, determing if a snippet containing nocut or softcut is to be generated. If not mentioned,
    it will generate soft cuts.
    '''
    def __init__(self, fps, framenum, nocut = False):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.csvpath = ''
        self.fps = fps
        self.framenum = framenum
        self.nocut = nocut

    def get_csv_path(self):
        '''
        Returns CSV file path generated by previous module, which is to be used to produce cuts snippets.
        '''
        self.csvpath = os.path.join(self.here, "results", "softcuts", "timestamps.csv")

    def read_csv(self):
        '''
        Function which reads CSV file containing timestamps, and pass the data to nocutdatamaker/softcutdatamaker 
        to generate the video snippet with no cut or soft cut respectively.
        '''
        with open(self.csvpath, 'r') as file:
            reader = csv.reader(file)
            print("Generating cut snippets...")
            for row in reader:
                timepairs = int((len(row) - 1) / 2)  #For Multiple Cuts
                init = 1
                for time in range(timepairs):
                    if self.nocut:
                        nocutdatamaker(row[0], row[init], row[init+1], self.fps, self.framenum).run()
                    else:
                        softcutdatamaker(row[0], row[init], row[init+1], self.fps, self.framenum).run()
                    init = init + 2

    def run(self):
        ################
        #DRIVER FUNCTION
        ################
        self.get_csv_path()
        self.read_csv()

if __name__=="__main__":
    reader(24, 50, False).run()
    reader(24, 50, True).run()