import os
import cv2
import csv
import json
import time
import datetime
import argparse
from cutdetector import predict

class run():
    def check_dir(self, iscsvframe=False, iscsvtime=False, ismepjson=False):
        here = os.path.dirname(os.path.abspath(__file__))
        if iscsvframe:
            outdir = os.path.join(here, "csv_cuts")
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
        if iscsvtime:
            outdir = os.path.join(here, "csv_shots")
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
        if ismepjson:
            outdir = os.path.join(here, "json_mep")
            if not os.path.isdir(outdir):
                os.mkdir(outdir)

        return outdir

    def sort_cuts(self, hc, sc):
        cuts = {**hc, **sc}
        cuts = dict(sorted(cuts.items()))
        return cuts

    def shot_time(self, cuts, length, fps):
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

    def csv_frames(self, outpath, cuts):
        with open(outpath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['index', 'frame', 'type'])
            count = 0
            for fr, typ in cuts.items():
                writer.writerow([count, fr, typ])
                count=count+1

    def csv_time(self, outpath, shots):
        with open(outpath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['index', 'start_frame', 'end_frame'])
            count = 0
            for shot in shots:
                writer.writerow([count, shot[0], shot[1]])
                count=count+1

    def mep_json(self, outdir, vidpath, filename, shots, length, height, width):
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

    def get_csvframes(self, vidpath, modpath, outdir):
        hc, sc = predict(0.75, 1, 100, modpath).run(vidpath, False)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, vidpath.split('/')[-1]+'.csv')
        self.csv_frames(outdir, cuts)
        return outdir

    def get_csvtime(self, vidpath, modpath, outdir):
        filename = vidpath.split('/')[-1].split('.')[0]
        cap = cv2.VideoCapture(vidpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        length = length/fps
        hc, sc = predict(0.75, 1, 100, modpath).run(vidpath, True)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, filename+'.csv')
        shots = self.shot_time(cuts, length, fps)
        self.csv_time(outdir, shots)
        return outdir

    def get_mepjson(self, vidpath, modpath, outdir):
        filename = vidpath.split('/')[-1].split('.')[0]
        cap = cv2.VideoCapture(vidpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        length = float("{:.2f}".format(length/fps))
        hc, sc = predict(0.75, 1, 100, modpath).run(vidpath, True)
        cuts = self.sort_cuts(hc, sc)
        outdir = os.path.join(outdir, filename+'.json')
        shots = self.shot_time(cuts, length, fps)
        self.mep_json(outdir, vidpath, filename, shots, length, height, width)
        return outdir

    def readonly(self, vidpath, modpath):
        hc, sc = predict(0.75, 1, 100, modpath).run(vidpath, True)
        return hc, sc

    def run(self, vidpath, modpath, iscsvframe=False, iscsvtime=False, ismepjson=False, readonly=False):
        if iscsvframe:
            outdir = self.check_dir(iscsvframe=True)
            filepath = self.get_csvframes(vidpath, modpath, outdir)
        if iscsvtime:
            outdir = self.check_dir(iscsvtime=True)
            filepath = self.get_csvtime(vidpath, modpath, outdir)
        if ismepjson:
            outdir = self.check_dir(ismepjson=True)
            filepath = self.get_mepjson(vidpath, modpath, outdir)
        if readonly:
            self.readonly(vidpath, modpath)