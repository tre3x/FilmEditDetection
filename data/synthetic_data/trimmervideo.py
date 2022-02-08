import os
import cv2
import csv
import random
import numpy as np

class softcutdatamaker():
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
        self.check_dir()

    def check_dir(self):
        '''
        Checks if the directory where videos snippets with soft cuts are to be stored, 
        are already present
        '''
        finaldatapath = os.path.join(self.here, "trim_video")
        if not os.path.isdir(finaldatapath):
            os.mkdir(finaldatapath)
        softcutpath = os.path.join(finaldatapath, "softcut")
        if not os.path.isdir(softcutpath):
            os.mkdir(softcutpath)
            
    def get_referenceframe(self, vidlength):
        '''
        Get reference frame about which trimming of the parent video is going to take place,
        to produce shorter video snippet with no cut in between.
        '''
        count = 0
        while True:
            frame = random.randint(self.initframe, self.finframe)
            if (vidlength - frame > self.framenum//2) and frame > self.framenum//2:
                return frame
            if count > 15:
                break
            count = count + 1
        
    def trim_video(self):
        '''
        Trims the parent video according to a reference frame to produce shorter video snippet
        of required frames, containg a soft cut in between.
        '''
        cap = cv2.VideoCapture(self.path)
        vidlength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ref_frame = self.get_referenceframe(vidlength)
        if ref_frame is not None:
            outpath = os.path.join(self.here, "trim_video", "softcut", self.path.split("/")[-1])
            
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))


            startframe = ref_frame - self.framenum//2
            framecount = startframe

            while framecount < startframe+self.framenum:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(framecount))
                res, frame = cap.read()
                out.write(frame)
                framecount = framecount + 1
            out.release()

    def run(self):
        self.trim_video()

class nocutdatamaker():
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
        self.cap = cv2.VideoCapture(self.path)
        self.check_dir()

    def check_dir(self):
        '''
        Checks if the directory where videos snippets with soft cuts are to be stored, 
        are already present
        '''
        finaldatapath = os.path.join(self.here, "trim_video")
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
        outpath = os.path.join(self.here, "trim_video", "nocut", self.path.split("/")[-1])
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))

        referenceframe = self.get_referenceframe()
        framecount = referenceframe
        while framecount < referenceframe+self.framenum:
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

class hardcutdatamaker():
    '''
    This class generates video snippets with hard cut in them, given
    INPUT : path, frame, fps, framenum
    path - path of the video file,
    frame - hardcut frame in the video,
    fps - required frames per seconds of the video snippet,
    framenum - number of frames to be present in the snippet
    '''
    def __init__(self, path, frame, fps, framenum):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.path = path
        self.referenceframe = int(frame)
        self.fps = fps
        self.framenum = framenum
        self.check_dir()

    def check_dir(self):
        '''
        Checks if the directory where videos snippets with hard cuts are to be stored, 
        are already present
        '''
        finaldatapath = os.path.join(self.here, "trim_video")
        if not os.path.isdir(finaldatapath):
            os.mkdir(finaldatapath)
        hardcutpath = os.path.join(finaldatapath, "hardcut")
        if not os.path.isdir(hardcutpath):
            os.mkdir(hardcutpath)
               
    def trim_video(self):
        '''
        Trims the parent video according to a reference frame to produce shorter video snippet
        of required frames, containg a hard cut in between.
        '''
        cap = cv2.VideoCapture(self.path)
        vidlength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ref_frame = self.referenceframe
        if ref_frame is not None:
            outpath = os.path.join(self.here, "trim_video", "hardcut", self.path.split("/")[-1])
            
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))


            startframe = ref_frame - self.framenum//2
            framecount = startframe

            while framecount < startframe+self.framenum:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(framecount))
                res, frame = cap.read()
                out.write(frame)
                framecount = framecount + 1
            out.release()

    def run(self):
        self.trim_video()


class reader():
    '''
    This class takes CSV timestamps generated by cutgenerator module, and generates snippets of given frame
    of soft cuts or not cut. This data is required for training the 3D CNNs. Results will be stored in
    'finaldata/nocut' or 'finaldata/softcut'.
    INPUT : csvpath, fps, framenum, softcut, hardcut, nocut
    csvpath - path of the previously generated csv file containing timestamps,
    fps - required frames per second of the snippet video,
    framenum - number of frames to be present in the snippet,
    hardcut - a boolean, determing if a snippet containing hardcut is to be generated. Default value False
    softcut - a boolean, determing if a snippet containing softcut is to be generated. Default value False
    nocut - a boolean, determing if a snippet containing nocut is to be generated. Default value False
    '''
    def __init__(self, fps, framenum, softcut=False, hardcut=False, nocut=False):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.csvpath = ''
        self.fps = fps
        self.framenum = framenum
        self.softcut = softcut
        self.hardcut = hardcut
        self.nocut = nocut

    def read_csv(self):
        '''
        Function which reads CSV file containing timestamps, and pass the data to nocutdatamaker/softcutdatamaker 
        to generate the video snippet with no cut or soft cut respectively.
        '''
        csvpath = ""
        if self.softcut:
            try:
                here = os.path.dirname(os.path.abspath(__file__))
                csvpath = os.path.join(here, "results", "softcuts", "timestamps.csv")
                if os.path.isfile(csvpath):
                    print("Generating soft-cut snippets...")
                else:
                    print("Soft-Cut Annotation CSV file not found!! Make sure the folder structure is correct.")
            except:
                print("Bad file found for softcut generation!!")

        if self.hardcut:
            try:
                here = os.path.dirname(os.path.abspath(__file__))
                csvpath = os.path.join(here, "results", "hardcuts", "timestamps.csv")
                if os.path.isfile(csvpath):
                    print("Generating hard-cut snippets...")
                else:
                    print("Soft-Cut Annotation CSV file not found!! Make sure the folder structure is correct.")
            except:
                print("Bad file found for hardcut generation!!")

        if self.nocut:
            try:
                here = os.path.dirname(os.path.abspath(__file__))
                csvpath = os.path.join(here, "results", "nocuts", "timestamps.csv")
                if os.path.isfile(csvpath):
                    print("Generating no-cut snippets...")
                else:
                    print("Soft-Cut Annotation CSV file not found!! Make sure the folder structure is correct.")
            except:
                print("Bad file found for nocut generation!!")

        if csvpath != "":
            with open(csvpath, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if self.nocut:
                        nocutdatamaker(row[0], float(row[1]), float(row[2]), self.fps, self.framenum).run()
                    if self.softcut:
                        softcutdatamaker(row[0], float(row[1]), float(row[2]), self.fps, self.framenum).run()
                    if self.hardcut:
                        hardcutdatamaker(row[0], float(row[1]), self.fps, self.framenum).run()

    def run(self):
        ################
        #DRIVER FUNCTION
        ################
        self.read_csv()

if __name__=="__main__":
    reader(24, 50, softcut=True).run()
