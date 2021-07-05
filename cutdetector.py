import os
from Models import hardcut, softcut

class predict():
    '''
    PREDICT THE FRAME INDEX OF CUTS PRESENT IN FILMS
    INPUT : threshold, child_process, model_path, vid_path
    threshold-threshold value for classifying a frame as hardcut
    in first module
    child_process-number of child process to be initiated in
    first module
    model_path-path of trained saved 3DDCNN model for soft cut 
    classification
    vid_path-target video path
    OUTPUT : hardcuts, softcuts
    hardcuts-frame index of hard cuts present
    softcuts-frame index of soft cuts present
    '''
    def __init__(self, threshold, child_process, model_path):
        self.threshold = threshold
        self.child_process = child_process
        self.model_path = model_path

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
        hardcuts, candidates = hardcut.get_result(vid_path, self.child_process, self.threshold)
        return hardcuts, candidates

    def get_softcuts(self, vid_path, candidates):
        '''
        FUNCTION TO CALL SOFT CUT DETECTOR DL MODULE
        INPUT : vid_path, candidates
        vid_path-target video path
        candidates-frame index of transition candidates
        OUTPUT : softcuts
        softcuts-frame index of soft cuts present
        '''
        softcuts = softcut.softcut(self.model_path).get_result(vid_path, candidates, 50)
        return softcuts

    def run(self, vid_path):
        '''
        DRIVER FUNCTION TO CALL THE MODULES
        INPUT : vid_path
        vid_path-target video path
        OUTPUT : hardcuts, softcuts
        hardcuts-frame index of hard cuts present
        softcuts-frame index of soft cuts present
        '''
        hardcuts, candidates = self.get_hardcuts(vid_path)
        softcuts = self.get_softcuts(vid_path, candidates)
        print("Hardcuts : {}".format(hardcuts))
        print("Candidates : {}".format(candidates))
        print("Softcuts : {}".format(softcuts))

        return hardcuts, softcuts

if __name__=='__main__':
    predict(0.75, 2, '/home/tre3x/Python/Red_Hen/Models/3DCNN').run('/home/tre3x/Python/Red_Hen/DatasetGenerator/MEPdata/a_babys_shoe.mp4')