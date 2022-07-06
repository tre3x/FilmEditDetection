import os
import csv
import sys, copy
import cv2

class snips():
    def __init__(self, csvpath, vidpath):
        here = os.path.dirname(os.path.abspath(__file__))
        self.csvpath = csvpath
        self.vidpath = vidpath
        if not os .path.isdir(os.path.join(here, "snips")):
            os.mkdir(os.path.join(here, "snips"))
        self.outpath =  os.path.join(here, "snips", ".".join(vidpath.split('/')[-1].split('.')[:-1]))

    def checkdir(self):
        if not os.path.isdir(self.outpath):
            os.mkdir(self.outpath)

    def stamp2second(self, stamp):
        st = stamp.split(':')
        return int(st[0])*(3.6*(10**6)) + int(st[1])*(6*(10**4)) + int(st[2])*(10**3) + int(st[-1])

    def midShotsIndex(self):
        cuts = []
        mids = []
        with open(self.csvpath, 'r') as csvfile:        
            datareader = csv.reader(csvfile)
            next(datareader)
            for row in datareader:
                cuts.append(self.stamp2second(row[1]))
            for index in range(len(cuts)):
                try:
                    mids.append(int((cuts[index] + cuts[index+1])/2))
                except:
                    pass
        return mids

    def store(self, window, frames):
        cap = cv2.VideoCapture(self.vidpath)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        for frame in frames:
            out = cv2.VideoWriter(os.path.join(self.outpath, "{}.avi".format(frame)), cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height), 0)
            for fr in range(frame-window//2, frame+window//2):
                cap.set(cv2.CAP_PROP_POS_MSEC, fr)
                res, frame = cap.read()
                out.write(frame)
            out.release()

    def gen(self, N):
        self.checkdir()
        window = N//2
        mids = self.midShotsIndex()
        self.store(window, mids)
        


class iterator():
    def __init__(self, vid_path):
        self.vidspath = vid_path
        self.csvspath = os.path.join(vid_path, "csv_s of B_W sheets per individual title")

    def storesnips(self, vid, N):
        try:
            vidpath = os.path.join(self.vidspath, vid+'.mp4')
            csvpath = os.path.join(self.csvspath, vid+' - Sheet1.csv')
            snips(csvpath, vidpath).gen(N)
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

if __name__=='__main__':
    iterator('/home/at02400@ens.ad.etsmtl.ca/FilmEditDetection/data/MEP_data/B_W films').run(100)

