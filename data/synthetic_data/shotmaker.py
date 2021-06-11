import cv2
import numpy as np
import os

class shotgenerator():
    def __init__(self, vidname, msbpath, fps, threshold_frame = 80):
        '''
        This class generates and stores individual shots of a video given the following 
        inputs : 
        INPUT : vidname, msbpath, fps, thereshold_frame
        vidname - Video filename according to the TRECVID IACC.3 dataset
        msbpath - Directory path of msb files containing shot boundary data
        fps : Set the Frames per Second of the generated shot
        threshold_frame - Set the threshold value for shot generation
        '''
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.msbpath = msbpath
        self.check_dir()
        self.outpath = os.path.join(self.here, "shots", vidname.split('._-o-_.')[1].rsplit('.', 1)[0])
        self.fps = fps
        self.threshold_frame = threshold_frame
        if not os.path.exists(self.outpath):
            os.makedirs(self.outpath)
            self.run(vidname)

    def check_dir(self):
        ########################################################
        #Create result directory where video shots will be stored
        ########################################################
        shotspath = os.path.join(self.here, "shots")
        if not os.path.isdir(shotspath):
            os.mkdir(shotspath)  
        
    def get_boundaries(self, timestamps): 
        '''
        Returns timestamps of video in list format given the msb timestamp file
        INPUT : timestamps
        timestamps - msb timestamp file path of the concerened video.
        OUPUT : times
        times - a list containg timestamps of the video in list format.
        '''
        timestamps = os.path.splitext(timestamps)[0] + '.msb'
        with open(timestamps, encoding = "ISO-8859-1") as f:
            times = f.readlines()[2:]
        f.close()    
        return times
    
    def shotmaker(self, start, end, videopath):
        '''
        Generates and stores individual shots in a video given start and end frame
        of the shots, and the videopath of the parent video. Shots are named with
        the starting frame of the shot.
        '''
        video = cv2.VideoCapture(videopath)
        framecount = start
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        outpath = os.path.join(self.outpath, str(start) + '.avi')
        out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height))
        while framecount <= end:
            video.set(1, framecount-1)
            res, frame = video.read()
            out.write(frame)
            framecount = framecount + 1
        out.release()

    def run(self, vidname):
        '''
        Check if the length of individual shots are greater than a threshold value.
        If yes, runs the shotmaker function to generate and store shots. 
        '''
        timestamps = os.path.join(self.msbpath, vidname)
        videopath = os.path.join(self.here, "videos", vidname.split('._-o-_.')[1])

        times = self.get_boundaries(timestamps)
        count = 1
        print("Generating Shots...")
        for boundary in times:
            start = int(boundary.split(" ")[0])
            end = int(boundary.split(" ")[1][:-1])
            if (end - start) > self.threshold_frame:
                self.shotmaker(start, end, videopath)   
                count+=1

if __name__ == '__main__':
    shotgenerator("Political_videos-GeorgeWBush20020321_6_312._-o-_.Political_videos-GeorgeWBush20020321_6_312_512kb.mp4", "/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/msb", 24)
