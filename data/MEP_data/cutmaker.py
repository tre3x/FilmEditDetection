import os
import csv
import cv2
import sys
import random
import numpy as np

class cut():
    def __init__(self, csvpath, vid_path):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.csvpath = csvpath
        self.vid_path = vid_path
        self.cap = cv2.VideoCapture(self.vid_path)

    def check_dir(self):
        cuts = ['nocut', 'softcut', 'hardcut']
        cutspath = os.path.join(self.here, "cuts")
        if not os.path.isdir(cutspath):
            os.mkdir(cutspath)
        for cut in cuts:
            cutpath = os.path.join(cutspath, cut)
            if not os.path.isdir(cutpath):
                os.mkdir(cutpath)  

    def timestamp2frame(self, time):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        timelist = time.split(":")
        frame = round(((int(timelist[0])* 3600) + (int(timelist[1])* 60) + int(timelist[2]) +(int(timelist[3])/1000))  * fps)
        return frame

    def get_cutstamps(self):
        cutstamp=[]
        with open(self.csvpath, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                t = self.timestamp2frame(row[1])
                cutstamp.append([t, row[2]])
        return cutstamp  

    def get_referenceframe(self, N, cutframes):
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        while True:
            frame = random.randint(N, length-N-1)
            for i in range(len(cutframes)-1):
                if frame-cutframes[i][0]>N//2 and cutframes[i+1][0]-frame>N//2:
                    return frame

    def getsnippet(self, frame, N, vidname, count, nocut=False, hardcut=False, softcut=False):
        if hardcut:
            dir_name = 'hardcut'
            ref_frame = frame
        elif softcut:
            dir_name = 'softcut'
            ref_frame = frame
        else:
            dir_name = 'nocut'
            ref_frame = self.get_referenceframe(N, frame)

        if ref_frame is not None:
            outpath = os.path.join(self.here, "cuts", dir_name, vidname+'_'+str(count)+'.mp4')
                
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            out = cv2.VideoWriter(outpath,cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            startframe = ref_frame - N//2
            framecount = startframe

            while framecount < startframe+N:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(framecount))
                res, frame = self.cap.read()
                out.write(frame)
                framecount = framecount + 1
            out.release()
        
        
    def cut_iterator(self, N, vidname):
        count = 1
        cuts = self.get_cutstamps()
        for cut in cuts:
            sys.stdout.write("\rCuts generated : {}/{}".format(count, len(cuts)))
            sys.stdout.write("\n")
            if cut[1].lower()=='hard':
                self.getsnippet(cut[0], N, vidname, count, hardcut=True)
            if cut[1].lower()=='soft':
                self.getsnippet(cut[0], N, vidname, count, softcut=True)
            self.getsnippet(cuts, N, vidname, count, nocut=True)
            sys.stdout.write("\033[F")
            count=count+1

    def make(self, N, vidname):
        self.check_dir()
        self.cut_iterator(N, vidname)


class iterator():
    def __init__(self, vid_path):
        self.vidspath = vid_path
        self.csvspath = os.path.join(vid_path, "csv_s of B_W sheets per individual title")

    def getcuts(self, vid, N):
        try:
            vidpath = os.path.join(self.vidspath, vid+'.mp4')
            csvpath = os.path.join(self.csvspath, vid+' - Sheet1.csv')
            cut(csvpath, vidpath).make(N, vid)
        except:
            pass

    def run(self, N):
        vidcount=1
        for vidname in os.listdir(self.vidspath):
            if vidname.endswith('.mp4'):
                vid = ".".join((vidname.split("/")[-1]).split('.')[:-1])

                sys.stdout.write("\r#{}/{}".format(vidcount, len(os.listdir(self.vidspath))-1))
                sys.stdout.write('\n')
                sys.stdout.write("\rGetting cuts of {}...".format(vid))
                sys.stdout.write('\n')
                
                self.getcuts(vid, N)

                sys.stdout.write("\033[F")
                sys.stdout.write("\033[F")
                vidcount=vidcount+1
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("\n")

if __name__=='__main__':
    print(iterator('/B_W films').run(50))