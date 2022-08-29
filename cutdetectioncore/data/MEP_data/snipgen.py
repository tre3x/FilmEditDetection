import os
import csv
import sys, copy
import cv2

class snips():
    def __init__(self, csvpath, vidpath):
        here = os.path.dirname(os.path.abspath(__file__))
        self.csvpath = csvpath
        self.vidpath = vidpath
        self.cap = cv2.VideoCapture(self.vidpath)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not os .path.isdir(os.path.join(here, "snips")):
            os.mkdir(os.path.join(here, "snips"))
        self.outpath =  os.path.join(here, "snips", ".".join(vidpath.split('/')[-1].split('.')[:-1]))

    def checkdir(self):
        if not os.path.isdir(self.outpath):
            os.mkdir(self.outpath)

    def stamp2index(self, stamp):
        st = stamp.split(':')
        sec =  int(st[0])*3600 + int(st[1])*60 + int(st[2]) + int(st[-1])/1000
        return int(sec*self.fps)

    def midShotsIndex(self):
        cuts = []
        mids = []
        with open(self.csvpath, 'r') as csvfile:        
            datareader = csv.reader(csvfile)
            next(datareader)
            for row in datareader:
                cuts.append(self.stamp2index(row[1]))
            for index in range(len(cuts)):
                try:
                    if cuts[index+1] - cuts[index] > self.window:
                        mids.append(int((cuts[index] + cuts[index+1])/2))
                except:
                    pass
        return mids

    def store(self, window, frames, target_fps):
        for frame in frames:
            out = cv2.VideoWriter(os.path.join(self.outpath, "{}.avi".format(frame)), cv2.VideoWriter_fourcc(*'XVID'), target_fps, (self.width, self.height))
            for fr in range(frame-window//2, frame+window//2):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, fr)
                res, frame = self.cap.read()
                out.write(frame)
            out.release()

    def gen(self, N, duration, target_fps):
        self.checkdir()
        self.window = N//2 + (target_fps*duration)//2
        mids = self.midShotsIndex()
        self.store(self.window, mids, target_fps)
        


class iterator():
    def __init__(self, vid_path, fps, duration):
        self.vidspath = vid_path
        self.fps = fps
        self.duration = duration
        self.csvspath = os.path.join(vid_path, "csv_s of B_W sheets per individual title")

        assert os.path.isdir(self.vidspath), 'MEP BW video dataset not found!!'
        assert os.path.isdir(self.csvspath), 'MEP CSV annotations not found!!'

    def storesnips(self, vid, N):
        try:
            vidpath = os.path.join(self.vidspath, vid+'.mp4')
            csvpath = os.path.join(self.csvspath, vid+' - Sheet1.csv')
            if not os.path.isfile(csvpath):
                print("CSV annotation file of {}.mp4 not found, skipping this video!".format(vid))
            snips(csvpath, vidpath).gen(N, self.duration, self.fps)
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
                
                self.storesnips(vid, N)

                sys.stdout.write("\033[F")
                sys.stdout.write("\033[F")
                vidcount=vidcount+1
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("\n")

