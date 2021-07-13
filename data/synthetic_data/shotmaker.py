import cv2
import random
import numpy as np
import os

class shotgenerator():
    def __init__(self, msbpath, fps, num_video = -1, threshold_frame = 80):
        '''
        This class generates and stores individual shots of a video given the following 
        inputs : 
        INPUT : msbpath, fps, num_video = -1, thereshold_frame
        msbpath : Directory path of msb files containing shot boundary data
        fps : Set the Frames per Second of the generated shot
        threshold_frame - Set the threshold value for shot generation
        '''
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.msbpath = msbpath
        self.check_dir()   
        self.fps = fps
        self.threshold_frame = threshold_frame

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

    def add_noise(self, frame):
        '''
        Adds random noise to an image.
        INPUT - frame
        frame:input frame where noise is to be added
        OUTPUT - noisy
        noisy:frame with added noise
        '''
        mean = 0
        var = np.random.uniform(0, 1.0)
        sigma = var**0.5
        row,col= frame.shape
        gauss = np.random.normal(mean,sigma,(row,col))
        gauss = gauss.reshape(row,col)
        noisy = frame + gauss
        noisy = np.uint8(noisy)
        return noisy     
    
    def shotmaker(self, start, end, videopath, outpath, noise):
        '''
        Generates and stores individual shots in a video given start and end frame
        of the shots, and the videopath of the parent video. Shots are named with
        the starting frame of the shot.
        '''
        video = cv2.VideoCapture(videopath)
        framecount = start
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        outpath = os.path.join(outpath, str(start) + '.avi')
        out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'XVID'), self.fps, (width, height), 0)
        while framecount <= end:
            video.set(1, framecount-1)
            res, frame = video.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            if noise:
                frame = self.add_noise(frame)
            out.write(frame)
            framecount = framecount + 1
        out.release()

    def run(self, vidname, outpath, noise):
        '''
        Check if the length of individual shots are greater than a threshold value.
        If yes, runs the shotmaker function to generate and store shots. 
        INPUT - vidname, outpath
        vidname : name of the video accoriding to TRECVID IACC.3 dataset xml file
        outpath : outpath path of the shots
        '''
        timestamps = os.path.join(self.msbpath, vidname)
        videopath = os.path.join(self.here, "videos", vidname)

        times = self.get_boundaries(timestamps)
        count = 1
        print("Generating Shots of Video-{} ...".format(vidname.split('._-o-_.')[1].rsplit('.', 1)[0]))
        for boundary in times:
            start = int(boundary.split(" ")[0])
            end = int(boundary.split(" ")[1][:-1])
            if (end - start) > self.threshold_frame:
                self.shotmaker(start, end, videopath, outpath, noise)   
                count+=1

    def iterator(self, num_video=-1, noise=False):
        '''
        Iterates videos in 'videos' folder created by the viddownlaod.py module.
        Call run function to create shots from all videos or specified number of videos.
        INPUT - num_video
        num_video : Number of videos in the videos folder to be considered to create shots. Defauult value = -1, all videos.
        '''
        downvideos_path = os.path.join(self.here, "videos")
        video_names = []
        for file in os.listdir("/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/videos"):
            if file.endswith(".mp4"):
                video_names.append(file)

        if num_video != -1:
            video_names = random.sample(video_names, num_video)

        for video in video_names:
            outpath = os.path.join(self.here, "shots", video.split('._-o-_.')[1].rsplit('.', 1)[0])
            if not os.path.exists(outpath):
                os.makedirs(outpath)
                self.run(video, outpath, noise)

if __name__ == '__main__':
    shotgenerator("/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/msb", 24).iterator(2, True)
