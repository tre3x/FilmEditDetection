import os
from model import hardcut, softcut

class predict():
    '''
    PREDICT THE FRAME INDEX OF CUTS PRESENT IN FILMS
    INPUT : threshold, child_process, N, model_path, vid_path
    threshold-threshold value for classifying a frame as hardcut
    in first module
    N-window size each candiate will be expanded into
    child_process-number of child process to be initiated in
    first module
    model_path-path of trained saved 3DDCNN model for soft cut 
    classification
    vid_path-target video path
    OUTPUT : hardcuts, softcuts
    hardcuts-frame index of hard cuts present
    softcuts-frame index of soft cuts present
    '''
    def __init__(self, threshold, child_process, N, model_path):
        self.threshold = threshold
        self.child_process = child_process
        self.N = N
        self.model_path = model_path

    def timestamps(self, seconds):
        int_sec = seconds//1
        float_sec = seconds%1
        hour = int(int_sec//3600)
        min = int((int_sec%3600)//60)
        sec = int((int_sec%3600)%60)
        milsec = float_sec*1000
        res = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2) + ":" + str(milsec)[:2]
        return res

    def get_timestamps(self, frames, fps):   
        fras = []
        for frame in frames:
            sec = frame/fps
            stamp = self.timestamps(sec)
            fras.append(stamp)
        return fras

    def get_seconds(self, frames, fps):
        fras = []
        for frame in frames:
            sec = frame/fps
            fras.append(sec)
        return fras

    def get_hardcuts(self, vid_path):
        '''
        FUNCTION TO CALL THE FIRST MODULE FOR HARD-CUT
        DETECTION
        INPUT : vid_path
        vidpath-target video path
        OUTPUT : hardcuts, candidates
        hardcuts-frame index of hard cuts present
        candidates-frame index of transition candidates
        '''
        hardcuts, candidates, fps = hardcut.get_result(vid_path, self.child_process, self.threshold)
        return hardcuts, candidates, fps

    def verify_cuts(self, vid_path, frames, ifSoftcut=False):
        '''
        FUNCTION TO CALL SOFT CUT DETECTOR DL MODULE
        INPUT : vid_path, candidates
        vid_path-target video path
        candidates-frame index of transition candidates
        OUTPUT : softcuts
        softcuts-frame index of soft cuts present
        '''
        if ifSoftcut:
            _, softcuts = softcut.softcut(self.model_path).getResult(vid_path, frames, self.N)
            return softcuts
        else:
            hardcut, _ = softcut.softcut(self.model_path).getResult(vid_path, frames, self.N)
            return hardcut

    def make_dict(self, frames, typ):
        dictionary = {}
        for frame in frames:
            dictionary.update({frame:typ})

        return dictionary

    def run(self, vid_path, timestamps=False):
        '''
        DRIVER FUNCTION TO CALL THE MODULES
        INPUT : vid_path
        vid_path-target video path
        OUTPUT : hardcuts, softcuts
        hardcuts-frame index of hard cuts present
        softcuts-frame index of soft cuts present
        '''
        hardcuts, candidates, fps = self.get_hardcuts(vid_path)
        hardcuts = self.verify_cuts(vid_path, hardcuts)
        softcuts = self.verify_cuts(vid_path, candidates, ifSoftcut=True)
        if timestamps:
            hardcuts = self.get_seconds(hardcuts, fps)
            candidates = self.get_seconds(candidates, fps)
            softcuts = self.get_seconds(softcuts, fps)
        hardcuts = self.make_dict(hardcuts, 'hard-cut')
        softcuts = self.make_dict(softcuts, 'soft-cut')
        print("All numbers denotes timestamps of cuts in seconds.")
        print("Hard-Cuts : {}".format(hardcuts))
        print("Soft-Cuts : {}".format(softcuts))
        
        return hardcuts, softcuts