import os
import cv2
import time
import random
import tensorflow as tf
from scipy import spatial
from functools import partial
import pathos.multiprocessing as mp
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import AveragePooling2D, Dense, Flatten


def get_vidobject(path):
    '''
    Function to get video object
    INPUT : path
    path-video path
    OUTPUT : cap
    cap-videocapture object of the video
    '''
    cap = cv2.VideoCapture(path)
    return cap

def get_fps(cap):
    '''
    Function to get FPS of video
    INPUT : cap
    cap-cv2.videocapture object of the video
    OUTPUT : fps
    fps-frames per second of the video
    '''
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    return fps

def readframe(cap, frame):
    '''
    Function to read frame given frame index and video object
    INPUT : cap, frame
    cap-cv2.videocapture object of the video
    frame-frame index of the target frame
    OUTPUT : frame
    frame-numpy array of the target frame
    '''
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    res, frame = cap.read()
    return frame

def get_framejumpunit(cap, cp):
    '''
    Function to create the range of groups during multiprocessing.
    INPUT : cap, cp
    cap-cv2.videocapture object of the video
    cp-number of processes initiated.
    OUTPUT : frame_jump_unit
    frame_jump_unit-the range of each group during multiprocessing
    '''
    frame_jump_unit = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // cp
    return frame_jump_unit

def model():
    '''
    Function to return the ResNet CNN model to be used for producing 
    feature maps
    OUTPUT : final_model
    final_model-model to be used for producing feature maps of video frames 
    '''
    model = ResNet50(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    output = model.layers[-1].output
    output = AveragePooling2D()(output)
    final_model = Model(inputs = model.input, outputs = output)
    return final_model

def get_feature(frame, model):
    '''
    Function to return feature map obtained by feeding the image to a CNN model.
    INPUT : frame, model
    frame-numpy array of the target frame to be featured
    model-model to be used to used for producing feature maps
    OUTPUT : map
    map-feature map obtained
    '''
    img = cv2.resize(frame, (224, 224))
    img = img.reshape(-1, 224, 224, 3)
    map = model.predict(img)
    map = map.flatten()
    return map

def get_similarity(map1, map2):
    '''
    Function to get spatial similarity measure between the feature maps. Feature maps are produced
    by siamese CNN model.
    INPUT : map1, map2
    map1-feature map of first image
    map2-feature map of second image
    OUTPUT : result
    result-similarity metric between two feature maps of the two images.
    '''
    result = 1 - spatial.distance.cosine(map1, map2)
    return result

def run_hardcutmetric(frame1, frame2, cnnmodel, cap):
    '''
    Driver function to get similarity between two frames
    INPUT : frame1, frame2, cnnmodel, cap
    frame1-index of first frame
    frame2-index of second frame
    cnnmodel-siamese model to be used to used for producing feature maps
    cap-cv2.videocapture object of the video
    OUTPUT : sim
    sim-similarity index between two frames
    '''
    frame1 = readframe(cap, frame1)
    frame2 = readframe(cap, frame2)
    map1 = get_feature(frame1, cnnmodel)
    map2 = get_feature(frame2, cnnmodel)
    sim = get_similarity(map1, map2)
    return sim

def timestamps(self, seconds):
    int_sec = seconds//1
    float_sec = seconds%1
    hour = int(int_sec//3600)
    min = int((int_sec%3600)//60)
    sec = int((int_sec%3600)%60)
    milsec = float_sec*1000
    res = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2) + ":" + str(milsec)[:2]
    return res

def findcandidate(fr, n, cnnmodel, thres, cap):
    '''
    Function to find hardcut or transition candidate frame whin a mini range of frames. This function
    can detect only one cut or cut candidate within the range. The approach to itearte through the mni range
    is inspired by binary search algorithm.
    Input : fr, n, cnnmodel, thres, cap
    fr-Initial frame from where checking is to be started
    n-range of frames upto which checking is to be done
    cnnmodel-siamese model to be used to used for producing feature maps
    thres-threshold value for classifying a frame as hard cut based on the distance metric
    cap-cv2.videocapture object of the video
    Output : 0/[a, d13, 1]/[a, d13, 0]
    0-no cut, control is passed to the initial frame of the next set of frames
    [a, d13, 1]-hardcut on frame a
    [a, d13, 0]-transition candidate on frame a
    '''
    a = fr
    b = fr + n
    flag = 0

    try:
        d13 = run_hardcutmetric(a, b, cnnmodel, cap)
        if(d13 > thres):
            return 0
        else:
            while True:
                mid = (a+b)//2
                d13 = run_hardcutmetric(a, b, cnnmodel, cap)
                if(b == a+1):
                    return [a, d13, 1]
                if(d13 > thres) and (flag == 1):
                    return [a, d13, 0]
                else:
                    flag = 1
                    d12 = run_hardcutmetric(a, mid, cnnmodel, cap) 
                    d23 = run_hardcutmetric(mid, b, cnnmodel, cap)
                    if(d12>d23):
                        a = mid
                    else:
                        b =  mid
    except:
        return 0

def run(path, cp, thres, group_number):
    '''
    Independent function to be run on different CPU cores for iterations through the trimmed range of
    video frames. Recevies a group number which decide the start and final frame the CPU core will
    iterate within. 
    INPUT : path, cp, thres, group_number
    path-Path of the video file
    cp-number of child process to be created for multiprocessing
    thres-threshold value for classifying a frame as hard cut based on the distance metric
    group_number - group number of the process to be perform on a CPU core independently. Decides
    the range of frame to compute upon.
    OUTPUT : hardcut, candidate
    hardcut:frame index of the hardcut frames
    candidate:frame index of transition candidate frame
    '''
    gpus = tf.config.list_physical_devices('GPU')
    try:
       for gpu in gpus:
           tf.config.experimental.set_memory_growth(gpu, True)
    except:
       pass
    
    cap = get_vidobject(path)
    n = get_fps(cap)
    frame_jump_unit = get_framejumpunit(cap, cp)
    cnnmodel = model()

    hardcuts = []
    candidates = []  
    init_frame = frame_jump_unit * group_number
    print("Path : {}, fps : {}".format(path, n))
    print("Running Hard-Cut detection module")
    for fr in range(init_frame, init_frame+frame_jump_unit, n):
        result = findcandidate(fr, n, cnnmodel, thres, cap)
        if not result:
             pass
        else:
            if result[2]:
                hardcuts.append(result[0])
            else:
                candidates.append(result[0])
    return [candidates, hardcuts]


def multi_run(path, cp, thres):
    '''
    Function for initiating multiple process on CPU cores. The task of iterating on the video frames
    is parallelized by different independent porcess on different cores.
    INPUT : path, chils_process, threshold
    path-Path of the video file
    child_process-number of child process to be created for multiprocessing
    thres-threshold value for classifying a frame as hard cut based on the distance metric
    OUTPUT : rt
    rt-appended list of output from all cores.
    '''
    print("Starting process on {} cores".format( min(mp.cpu_count(), cp)) )
    func = partial(run, path, cp, thres)
    p = mp.Pool()
    rt = p.map(func, range(cp))
    p.close()
    return rt

def get_result(path, child_process, threshold):
    '''
    Driver function for calling the hard cut detector module. Calls multi run module to
    initiate multiprocessing units.
    INPUT : path, chils_process, threshold
    path-Path of the video file
    child_process-number of child process to be created for multiprocessing
    threshold-threshold value for classifying a frame as hard cut based on the distance metric
    OUTPUT : hardcut, candidate
    hardcut:frame index of the hardcut frames
    candidate:frame index of transition candidate frame to be passed to next module
    '''
    #results = multi_run(path, child_process, threshold) MULTIPROCESSING NOT WORKING WITH FLASK
    results = run(path, 1, threshold, 0)
    
    cap = get_vidobject(path)
    fps = get_fps(cap)

    hardcut = []
    candidate = []
    '''
    MULTIPROCESSING NOT WORKING WITH FLASK
    for result in results:
        hardcut = hardcut + result[1]
        candidate = candidate + result[0]
    '''
    for hcs in results[1]:
        hardcut.append(hcs)
    for scs in results[0]:
        candidate.append(scs)
    return hardcut, candidate, fps

if __name__=='__main__':
    child_process = 4 #Number of child process
    threshold = 0.75
    path = "/home/tre3x/Python/FilmEditsDetection/uploads/Classmates_1914_22.mp4"

    start = time.time()
    r = get_result(path, child_process, threshold)
    end= time.time()

    print("Hardcuts : {}".format(r[0]))
    print("Candidate : {}".format(r[1]))
    print("Time taken : {}".format(end-start))
