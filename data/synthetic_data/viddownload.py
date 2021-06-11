import os
import xml.etree.ElementTree as ET
import urllib.request
import random
from shotmaker import shotgenerator

'''
Download videos in video folder and calls shotmaker.py to
create shots.
'''


class downloader():
    def __init__(self, xmlpath, msbpath, num):
        '''
        This class downloads 'num' number of random videos and call the shotmaker
        module for generatig individual shots.
        INPUT : filepath, num
        xmlpathpath - path of TRECVID IACC.3 dataset xml file
        msbpath - directory path of msb files containing shot boundary data
        num - number of random videos to be downloaded and broken into shots
        '''
        tree = ET.parse(xmlpath)
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.msbpath = msbpath
        self.root = tree.getroot()
        self.create_dir()
        self.video_selector(num)

    def create_dir(self):
        ########################################################
        #Create result directory where videos will be downloaded
        ########################################################
        videospath = os.path.join(self.here, "videos")
        if not os.path.isdir(videospath):
            os.mkdir(videospath)

    def video_downloader(self, index):
        '''
        Download videos given the index of the video file in  TRECVID IACC.3 dataset.
        Also calls the shotmaker module to make break and store the downloaded video
        into individual shots
        '''
        filename = self.root[index][1].text
        filesource = self.root[index][3].text
        link = filesource + "/" + filename.split('._-o-_.')[1]
        videopath = os.path.join(self.here, "videos", filename.split('._-o-_.')[1])
        if not os.path.exists(videopath):
            try:
                urllib.request.urlretrieve(link, videopath) 
                shotgenerator(filename, self.msbpath, 24)
            except:
                pass

    def video_selector(self, num):
        ########################################################################
        #Selects 'num' number of random video index from TRECVID IACC.3 dataset.
        ########################################################################
        index = random.sample(range(0, len(self.root)-1), num)
        count = 1
        for ind in index:
            print("###DOWNLOADING VIDEO " + str(count) + "###")
            print("This may take a while.")
            self.video_downloader(ind)
            count += 1

if __name__ == '__main__':
    downloader('iacc.3.collection.xml',  "/home/tre3x/Python/FilmEditsDetection/data/synthetic_data/msb", 2)
    