import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import cv2
import numpy as np
import tensorflow as tf
from tqdm import tqdm
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

class expand_frame():
  '''
  CREATE A WINDOW OF N ADJACENT FRAMES, GIVEN A REFERENCE FRAMES 
  THIS WINDOW(SMALL SNIPPET OF THE VIDEO) IS USED FOR EVALUATION 
  OF SOFT CUTS
  INPUT : path, ref, N
  path-path of the video
  ref-reference frame number
  N-size of window to be created
  OUTPUT : out
  OUT-window of frames, of size N
  '''
  def __init__(self, path):
    self.path = path

  def get_vidobj(self):
    '''
    FUNCTION TO GET VIDEO OBJECT
    OUTPUT : cap
    cap-videocapture object of the video
    '''
    cap = cv2.VideoCapture(self.path)
    return cap

  def read_frame(self, cap, frame):
    '''
    FUNCTION TO READ A PARTICULAR FRAME
    INPUT : cap, frame
    cap-cv2 video object
    frame-target frame number
    OUTPUT : frame
    frame-frame in form of numpy array
    '''
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    res, frame = cap.read()
    frame = cv2.resize(frame, (27, 48))
    return frame

  def trim_video(self, cap, start, end):
    '''
    FUNCTION TO CREATE NUMPY ARRAY OF FRAMES GIVEN
    BOUNDARIES. BASICALLY TRIMMING THE ORIGINAL VIDEO
    INTO SHORTER VIDEO.
    INPUT : cap, start, end
    cap-cv2 video object
    start-start frame in the original video reference
    end-end frames in the original video reference
    OUTPUT : frs
    frs-numpy array of frames
    '''
    frs = []
    for fr in range(start, end):
      frs.append(self.read_frame(cap, fr))

    return np.array(frs)

  def get_bdfr(self, cap, ref, N):
    '''
    FUNCTION TO GET BOUNDARY FRAMES IN WHICH WINDOW IS TO
    BE TRIMMED
    INPUT : cap, ref, N
    cap-cv2 video object
    ref-reference frame number
    N-size of window to be created
    OUTPUT : start, end
    start-start frame in the original video reference
    end-end frames in the original video reference
    '''
    len = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not N%2:
      rightN = (N//2)
      leftN = (N//2)
    else:
      rightN = (N//2)
      leftN = (N//2)+1
    if ref>=rightN  and len-ref>=leftN:
      start = ref-rightN
      end = ref+leftN
    elif ref<rightN  and len-ref>=leftN:
      start = 0
      end = ref+leftN+(rightN-ref)
    elif ref>=rightN  and len-ref<=leftN:
      start = ref-rightN-(leftN-(len-ref))
      end = len

    return start, end

  def run(self, ref, N):
    '''
    DRIVER FUCNTION TO CALL expand_frame FUNCTIONS
    INPUT : ref, N
    ref-reference frame number about which video will be trimmed
    N-size of window to be created
    OUTPUT : out
    out-numpy array of window of frames
    '''
    vid = self.get_vidobj()

    start, end = self.get_bdfr(vid, ref, N)
    out = self.trim_video(vid, start, end)
    out = out.reshape(-1, N, 48, 27, 3)
    return out

class softcut():
    '''
    MODULE TO PREDICT IF A SET OF FRAMES ARE SOFT CUTS
    OR HARDCUTS
    INPUT : model_path, video_path, frames
    model_path-trained saved model path of 3DDCNN model
    video_path-target video path
    frames-set of candiate frames to be analysed
    conf-dictionary containing configuration of the network
    '''
    def __init__(self, model_path, config):
        self.model_path = model_path
        self.config = config

    def getType(self, inp, _mod):
        '''
        BOOLEAN FUNCTION PREDICTING IF A GIVEN WINDOW OF FRAMES
        IS SOFT CUT OR HARDCUT
        INPUT : inp, _mod
        inp-input video path
        _mod-3DDCNN model
        OUTPUT : pred
        pred-boolean value depicting if a window is softcut
        '''
        pred = np.argmax(_mod.predict(inp))
        return pred
    
    def getResult(self, video_path, frames):
        '''
        DRIVER FUNCTION TO ITERATE THROUGH THE CANDIDATES AND ANALYSING
        EACH CANDIDATE BY EXPANDING IT INTO A WINDOW OF FRAMES.
        INPUT : video_path, frames, N
        video_path-target video path
        frames-set of candiate frames to be analysed
        OUTPUT : res
        res-list of candidate frames which lies in any soft cut region
        '''
        hard = []
        soft = []
        print("Running validation module...")
        mod = tf.keras.models.load_model(self.model_path)
        for frame in tqdm(frames, leave=False):
            snip = expand_frame(video_path).run(frame, self.config['soft-cut detector']['window_size'])
            cutType = self.getType(snip, mod)
            if cutType==0:
              hard.append(frame)
            if cutType==2:
              soft.append(frame)  
        return hard, soft

if __name__=='__main__':
    out = softcut('/3DCNN').getResult('/16.avi', [100, 150, 200, 250, 300, 315], 50)
    print(out)