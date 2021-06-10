import os
import csv
import cv2
import glob
import random
import numpy as np

class cutgenerator():
    '''
    This class generates one hard cuts and soft cut in a video from 
    two video shots given
    INPUT : shot1path, shot2path, outpath, gradualcut, fps, duration
    shot1path - path of video shot1,
    shot2path - path of video shot2,
    outpath - path of generated output video,
    gradual cut - a boolean, determining if a soft cut is to be generated,
    fps - required frames per second of the output video,
    duration - duration of soft cut if a soft cut is to be generated, otherwise 
    ignored 
    '''
    def __init__(self, shot1path, shot2path, outpath, gradualcut, fps, duration = 0):
        self.shot1 = cv2.VideoCapture(shot1path)
        self.shot2 = cv2.VideoCapture(shot2path)
        self.length1 = int(self.shot1.get(cv2.CAP_PROP_FRAME_COUNT))
        self.length2 = int(self.shot2.get(cv2.CAP_PROP_FRAME_COUNT))
        self.height = int(self.shot1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.shot1.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = fps
        self.out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (self.width, self.height), 0)
        self.alpha = 1
        self.gradualcut = gradualcut
        if gradualcut: self.duration = duration
        else:  self.duration = 1/self.fps            #In case of Hard cut, change occur in one frame
        self.create_video()

    def write_video(self, shotobj):
        '''
        Write original shots without transition to output video.
        INPUT : shotobj
        shotobj - Video object of the shot to be written in an 
        output video
        '''
        while True:
            ret, frame = shotobj.read()
            if ret==False:
                break
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                self.out.write(frame)

    def create_transition(self):
        '''
        Creates transition given two video shot objects, required
        frames per seconds, and duration of the cut(if soft cut).
        '''
        alpha = self.alpha
        while(alpha >= 0):
            self.shot1.set(cv2.CAP_PROP_POS_FRAMES, self.length1-1)
            res1, frame1 = self.shot1.read()
            self.shot2.set(cv2.CAP_PROP_POS_FRAMES, 0)
            res2, frame2 = self.shot2.read()
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            frame2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            frame = np.add((frame1*alpha), (frame2*(1-alpha))).astype(np.uint8) #Intermediate frame = F1*α + F2*(1-α), α ∈ [0, 1] in soft cut and α = {1,0} in hard cuts.
            alpha = alpha - (1/(self.fps * self.duration))
            self.out.write(frame)

    def create_video(self):
        ################
        #DRIVER FUNCTION
        ################
        self.write_video(self.shot1)                    #Writing shot1
        self.create_transition()                        #Creating intermediate transition
        self.write_video(self.shot2)                    #Writing shot2
        self.out.release()                              #We got a video with synthetic cut!


class runner():
    '''
    This class gets paths of all video shots present, and iterates through the number of 
    hard cuts and soft cuts required, taking two video shot path at a time at random. The selected two 
    video shot path are passed to the cutgenerator class for generating required type of cut within 
    two videos. Also, a csv file is generated with labels of timestamp of the cut within the videos.
    INPUT : numhard, numgradual, fps, duration
    numhard - number of hard cut videos required,
    numgradual - number of soft cut videos required,
    fps - required frames per second of the video,
    duration - duration of the soft cuts, if soft cuts is to be generated.
    '''
    def __init__(self, numhard, numgradual, fps, duration = 0):
        self.files = []
        self.numhard = numhard
        self.numgradual = numgradual
        self.fps = fps
        self.duration = duration
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.shotpath = os.path.join(self.here, "shots")
        self.dircheck()
        self.transmaker()

    def dircheck(self):
        '''
        Checks if the directory where videos with cuts are already present
        '''
        resultpath = os.path.join(self.here, "results")
        if os.path.isdir(resultpath):
            hardcutpath = os.path.join(resultpath, "hardcuts")
            softcutpath = os.path.join(resultpath, "softcuts")
            if not os.path.isdir(hardcutpath):
                os.mkdir(hardcutpath)
            if not os.path.isdir(softcutpath):
                os.mkdir(softcutpath)
        else:
            os.mkdir(resultpath)
            hardcutpath = os.path.join(resultpath, "hardcuts")
            softcutpath = os.path.join(resultpath, "softcuts")
            os.mkdir(hardcutpath)
            os.mkdir(softcutpath)

    def getshots(self):
        '''
        Gets path of all video shots present/generated by the previous
        'shotmaker' module.
        '''
        for x in os.walk(self.shotpath):
            for y in glob.glob(os.path.join(x[0], '*.avi')):
                self.files.append(y)

    def csv_hardcuttimestamps(self, outpath, shot):
        ''' 
        Generates CSV files containing timestamps/frame number of hard cuts.
        In case of hard cut, frame of the hard cut = number of frame in the first video shot
        INPUT : outpath, shot
        outpath - path of the csv file to be generated
        shot - video object of the first shot to be present in the final video with cut.
        '''
        shot = cv2.VideoCapture(shot)
        length = int(shot.get(cv2.CAP_PROP_FRAME_COUNT))
        out = os.path.join(self.here, "results", "hardcuts", 'timestamps.csv')
        fr = length 
        with open(out, 'a', newline='') as file:
            writer = csv.writer(file)   
            writer.writerow([outpath, fr])

    def csv_softcuttimestamps(self, outpath, shot):
        ''' 
        Generates CSV files containing timestamps/frame number of soft cuts, given the inputs,
        frames per second, and the duration of the softcut.
        Timestamps denotes the middle framne of the soft cut.
        So, frame of the hard cut = number of frame in the first video shot + (number of frames in soft cut)//2
        INPUT : outpath, shot
        outpath - path of the csv file to be generated
        shot - video object of the first shot to be present in the final video with cut.
        '''
        shot = cv2.VideoCapture(shot)
        length = int(shot.get(cv2.CAP_PROP_FRAME_COUNT))
        out = os.path.join(self.here, "results", "softcuts", 'timestamps.csv')
        fr = length   
        with open(out, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([outpath, fr, fr+(self.duration*self.fps)])
        
    def transmaker(self):
        '''
        Driver function which call the getchots mfunction to get all the paths of the video shots.
        Also, iterates through the number of hard cuts and soft cuts required, taking two video shot 
        path at a time at random. The selected two video shot path are passed to the cutgenerator class 
        for generating required type of cut within two videos.
        '''
        self.getshots()

        print("Generating hard cuts...")
        for i in range(self.numhard):
            index = random.sample(range(0, len(self.files)-1), 2)
            outpath = os.path.join(self.here, "results", "hardcuts", str(i) + ".avi")
            self.csv_hardcuttimestamps(outpath, self.files[index[0]])
            cutgenerator(self.files[index[0]], self.files[index[1]], outpath, False, self.fps)
            
        print("Generating soft cuts...")
        for i in range(self.numgradual):
            index = random.sample(range(0, len(self.files)-1), 2)
            outpath = os.path.join(self.here, "results", "softcuts", str(i) + ".avi")
            self.csv_softcuttimestamps(outpath, self.files[index[0]])
            cutgenerator(self.files[index[0]], self.files[index[1]], outpath, True, self.fps, self.duration)

if __name__ == '__main__':
    runner(20, 20, 24, 1)