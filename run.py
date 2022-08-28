import os
import cv2
import csv
import json
import time
import requests
import datetime
import argparse
from cutdetector import predict

class run():
    def __init__(self, conf):
        self.conf = conf

    def check_dir(self, outdir):
        #Creates output directory if not present
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

    def sort_cuts(self, hc, sc):
        #Sort cuts according to timestamps
        cuts = {**hc, **sc}
        cuts = dict(sorted(cuts.items()))
        return cuts

    def shot_time(self, cuts, length, fps):
        #Creates a list of start and end timestamps of shots
        shots = []
        if len(list(cuts.items())) >= 1:
            first = 0
            second = float("{:.2f}".format(list(cuts.keys())[0]))
            shots.append([first, second])
        for k in range(0, len(list(cuts.items()))-1):
            first = float("{:.2f}".format(list(cuts.keys())[k]))
            second = float("{:.2f}".format(list(cuts.keys())[k+1]))
            transition = float("{:.2f}".format(50/fps))
            if list(cuts.values())[k]=='hard-cut' and list(cuts.values())[k+1]=='hard-cut':
                shots.append([first, second])
            if list(cuts.values())[k]=='soft-cut' and list(cuts.values())[k+1]=='hard-cut':
                shots.append([first+transition, second])
            if list(cuts.values())[k]=='hard-cut' and list(cuts.values())[k+1]=='soft-cut':
                shots.append([first, second-transition])
            if list(cuts.values())[k]=='soft-cut' and list(cuts.values())[k+1]=='soft-cut':
                shots.append([first+transition, second-transition])

        if len(list(cuts.items())) >= 1:
            if list(cuts.values())[-1]=='soft-cut':
                shots.append([second+float("{:.2f}".format(50/fps)), float("{:.2f}".format(length))])
            else:
                shots.append([second, float("{:.2f}".format(length))])
        else:
            shots.append([0, float("{:.2f}".format(length))])

        return shots
    
    def shot_duration(self, cuts, length, fps):
        #Creates a list of duration of shots
        duration = []
        transition = float("{:.2f}".format(50/fps))
        if len(list(cuts.items())) > 1:
            if list(cuts.values())[0] == 'hard-cut':
                duration.append(float("{:.2f}".format(list(cuts.keys())[0])))
            if list(cuts.values())[0] == 'soft-cut':
                duration.append(float("{:.2f}".format(list(cuts.keys())[0]))-transition)

            for k in range(0, len(list(cuts.items()))-1):
                first = float("{:.2f}".format(list(cuts.keys())[k]))
                second = float("{:.2f}".format(list(cuts.keys())[k+1]))
                if list(cuts.values())[k]=='hard-cut' and list(cuts.values())[k+1]=='hard-cut':
                    duration.append(second-first)
                elif list(cuts.values())[k]=='soft-cut' and list(cuts.values())[k+1]=='hard-cut':
                    duration.append(second-first-2*(transition))
                else:
                    duration.append(second-(first+transition))

        return duration

    def csv_frames(self, outpath, cuts):
        #Writes a CSV file with frame index of cuts
        with open(outpath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['index', 'frame', 'type'])
            count = 0
            for fr, typ in cuts.items():
                writer.writerow([count, fr, typ])
                count=count+1

    def csv_time(self, outpath, shots):
        #Writes a CSV file with timestamps of start and end frames
        with open(outpath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['index', 'start_frame', 'end_frame'])
            count = 0
            for shot in shots:
                writer.writerow([count, shot[0], shot[1]])
                count=count+1

    def mep_json(self, outdir, vidpath, filename, shots, length, height, width):
        #Writes a JSON file formatted with MEP web annotation, containing 
        #timestamps of start and end timestanps of shots
        here = os.path.dirname(os.path.abspath(__file__))
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        str_shots=""
        for k, shot in enumerate(shots):
            if k!=len(shots)-1:
                str_shot = "{} {}, ".format(shot[0], shot[1])
            else:
                str_shot = "{} {}".format(shot[0], shot[1])
            str_shots = str_shots + str_shot
             
        with open(os.path.join(here, "sample_json", "MEP_sample.json")) as f:
            sample = json.load(f)

            sample['id'] = outdir
            sample['label']['en'][0] = ["Annotations for \"{}\"".format(filename)]
            sample['items'][0]['id'] = "{}#canvas".format(outdir)
            sample['items'][0]['height'] = height
            sample['items'][0]['width'] = width
            sample['items'][0]['duration'] = length
            sample['items'][0]['content'][0]['id'] = vidpath
            sample['items'][0]['content'][0]['height'] = height
            sample['items'][0]['content'][0]['width'] = width
            sample['items'][0]['content'][0]['duration'] = length
            sample['items'][0]['content'][0]['label']['en'] = "{}".format(filename)

            items = sample['items'][0]['items'][0]['items']
            count=1
            for shot in shots:
                item = {'id': "{}#scene{}".format(outdir, count), 
                'type': 'Annotation', 
                'generator': 'https://github.com/tre3x/FilmEditDetection', 
                'motivation': 'highlighting', 
                'creator': {'type': 'Agent', 'nickname': 'FilmEditDetector'}, 
                'created': st, 
                'rights': 'http://creativecommons.org/licenses/by/4.0/', 
                'target': {
                    'source': vidpath, 
                    'type': 'SpecificResource', 
                    'selector': 
                    {
                        'type': 'FragmentSelector', 
                        'conformsTo': 'http://www.w3.org/TR/media-frags/', 
                        'value': "t={},{}".format(shot[0], shot[1])
                        }
                    }
                    }

                items.append(item)
                count=count+1

        with open(outdir, 'w', encoding='utf-8') as f:
            json_string = json.dump(sample, f, ensure_ascii=False, indent=4)

    def cinemetrics(self, outpath, cuttimestamp, shotduration, length, submit, cine_details):
        #Writes a .cms file which supports cinemetrics (http://www.cinemetrics.lv/)
        totduration = 0
        iterator = 1
        shotlist = []
        for shot in shotduration:
            totduration = totduration + shot
        totduration = 10*totduration                    
        avgshotlength = 10*(totduration/len(shotduration))

        for duration, cuttime in zip(shotduration, cuttimestamp):
            shotlist.append("{};{:.2f};{:.2f};0".format(iterator, 10*duration, 10*cuttime))
            iterator = iterator+1  
        mdata = '\n'.join(shotlist)

        with open(outpath, 'w', newline='') as cmsfile:
            cmsfile.write("1\n")
            cmsfile.write("{}\n".format(len(cuttimestamp)))
            cmsfile.write("{}\n".format(avgshotlength))
            cmsfile.write("{}\n".format(length))
            cmsfile.write("BCU;CU;MCU;MS;MLS;FS;LS;Other\n")
            cmsfile.write("0;0;0;0;0;0;0;0\n")
            cmsfile.write("0;0;0;0;0;0;0;0\n")
            cmsfile.write("&@")
            cmsfile.write(mdata)

        if submit:
            CINEMETRICS_API_ENDPOINT = "http://www.cinemetrics.lv/submit.php"
            data = {'yname':cine_details['yname'],
                    'mtitle':cine_details['mtitle'],
                    'myear':cine_details['myear'],
                    'email':cine_details['email'],
                    'comments':'',
                    'mdata':mdata,
                    'simple':1,
                    'numshots':len(shotduration),
                    'asl':avgshotlength,
                    'filmlength':totduration }

            r = requests.post(url = CINEMETRICS_API_ENDPOINT, data=data)
            if r.status_code==200:
                print("Sumbitted to cinemetrics with status code 200")
            else:
                print("Cannot submit to cinemetrics server. Error Code {}".format(r.status_code))

    def get_csvframes(self, vidpath, modpath, outdir):
        #Driver function to write csv format with cuts frame index
        filename = vidpath.split('/')[-1].split('.')[0]
        hc, sc = predict(self.conf, modpath).run(vidpath, False)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, filename+'.csv')
        self.csv_frames(outdir, cuts)
        return outdir

    def get_csvtime(self, vidpath, modpath, outdir):
        #Driver function to write CSV format with start and end timestamps
        # of shots
        filename = vidpath.split('/')[-1].split('.')[0]
        cap = cv2.VideoCapture(vidpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        length = length/fps
        hc, sc = predict(self.conf, modpath).run(vidpath, True)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, filename+'.csv')
        shots = self.shot_time(cuts, length, fps)
        self.csv_time(outdir, shots)
        return outdir

    def get_mepjson(self, vidpath, modpath, outdir):
        #Driver function to write MEP web annotation JSON format
        filename = vidpath.split('/')[-1].split('.')[0]
        cap = cv2.VideoCapture(vidpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        length = float("{:.2f}".format(length/fps))
        hc, sc = predict(self.conf, modpath).run(vidpath, True)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, filename+'.json')
        shots = self.shot_time(cuts, length, fps)
        self.mep_json(outdir, vidpath, filename, shots, length, height, width)
        return outdir

    def get_cinemetrics(self, vidpath, modpath, outdir, submit, cine_details):
        #Driver function to write cinemetrics formatted output
        filename = vidpath.split('/')[-1].split('.')[0]
        cap = cv2.VideoCapture(vidpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        length = int(cap.get(cv2.CAP_PROP_FPS))
        length = float("{:.2f}".format(length/fps)) #length in second
        hc, sc = predict(self.conf, modpath).run(vidpath, True)
        cuts = self.sort_cuts(hc, sc)
        outpath = os.path.join(outdir, filename+'.cms')
        shotsduration = self.shot_duration(cuts, length, fps)
        self.cinemetrics(outpath, cuts, shotsduration, length, submit=submit, cine_details=cine_details)
        return

    def readonly(self, vidpath, modpath):
        #Driver function to show only cut timestamps in command line
        hc, sc = predict(self.conf, modpath).run(vidpath, True)
        return hc, sc

    def run(self, vidpath, modpath, outdir, iscsvframe=False, iscsvtime=False, ismepjson=False, readonly=False, iscinemetrics=False, submit=False, cine_details={}):
        #Driver function 
        if not readonly:
            self.check_dir(outdir)
            if iscsvframe:
                filepath = self.get_csvframes(vidpath, modpath, outdir)
            if iscsvtime:
                filepath = self.get_csvtime(vidpath, modpath, outdir)
            if ismepjson:
                filepath = self.get_mepjson(vidpath, modpath, outdir)
            if iscinemetrics:
                filepath = self.get_cinemetrics(vidpath, modpath, outdir, submit, cine_details)
        else:
            self.readonly(vidpath, modpath)