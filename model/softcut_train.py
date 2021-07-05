import os
import cv2
import numpy as np
import tensorflow as tf
from softcut_model import model
from softcut_data import softcut_data

class softcut():
    '''
    TRAINING THE SOFT CUT DETECTOR MODEL TO CLASSIFY A VIDEO SEGMENT AS SOFTCUT
    INPUT : train_path, test_path, SDDCNN, DDCNN, F, inputdim, batch_size
    train_path-directory path of training video files
    test_path-directory path of test video files
    SDDCNN-number of stacked dilated CNN blocks
    DDCNN-number of dilated CNN blocks
    F-number of filters/channels to be produced by convnets
    inputdim-Input dimension of series of frames of the video. Dimension-(framenumber, height, width, channel)
    batch_size-batch size for training the model   OUTPUT-_mod
    _mod-trained model for prediction

    To train the model - softcut(train_path, test_path, SDDCNN, DDCNN, F, inputdim).train(batch_size, epoch, steps, step_val, save, path)
    '''
    def __init__(self, train_path, test_path, SDDCNN, DDCNN, F, inputdim):
        self.train_path = train_path
        self.test_path = test_path
        self.F = F
        self.DDCNN = DDCNN
        self.SDDCNN = SDDCNN
        self.inputdim = inputdim

    def get_data(self):
        '''
        DATA PIPELINE
        RETURNS VIDEO DATA PATHS WITH LABEL
        OUTPUT : train_data, test_data
        train_data-training video data path with labels
        test_data-test video data path with labels
        '''
        train_data = softcut_data().load_traindata(self.train_path)
        test_data = softcut_data().load_testdata(self.test_path)
        return train_data, test_data

    def get_model(self):
        '''
        Calls the 3DDCNN model to be trained
        OUTPUT : mod
        mod-3DDCNN model
        '''
        mod = model(self.SDDCNN, self.DDCNN, self.F).call(self.inputdim)
        return mod

    def read_video(self, path):
        '''
        RETURNS VIDEO SEGMENT IN FORM OF NUMPY ARRAY
        INPUT : path
        path-target video path
        OUTPUT : frames
        frames-numpy array of video frames in a video segment
        '''
        frames = []
        cap = cv2.VideoCapture(path)
        while(True):
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (self.inputdim[1], self.inputdim[2]))
                frames.append(frame)
            else:
                break
        return frames

    def video_generator(self, batch_size, train):
        '''
        GENERATOR FUNCTION FOR FEEDING DATA INTO THE MODEL 
        WHILE TRAINING/TESTING
        INPUT : batch_size, train
        batch_size-batch_size of the data
        train-boolean value determining whether training or test is to be performed
        OUTPUT : batch_x, batch_y
        batch_x-video snippets of batch size in form of numpy array
        batch_y-label of the video snippers in form of umpy array 
        '''
        while True:
            if train:
                data, _ = self.get_data()
            else:
                _, data = self.get_data()
            batch = data[np.random.choice(data.shape[0], 32, replace=False), :]
            batch_x = []
            batch_output = [] 
            
            for elem in batch:
                input = np.array(self.read_video(elem[0]))
                output = elem[1]
                batch_x.append(input)
                batch_output.append(output)
            batch_x = np.array(batch_x)
            batch_y = np.array(batch_output)
            yield batch_x, batch_y

    def train(self, batch_size, epoch, steps, step_val, save=False, path='/'):
        '''
        DRIVER CODE FOR TRAINING THE MODEL
        INPUT : batch_size, epoch, steps, step_val, save, path
        batch_size-batch size of the data
        epoch-training epoch
        steps-training steps per epoch
        steps_val-validation steps per epoch
        save-boolean value stating if the model is to be saved. Default value is False
        path-path of the saved model
        OUTPUT :  _mod
        _mod-trained model
        '''
        _mod = self.get_model()
        _mod.compile('Adam', loss = tf.keras.losses.categorical_crossentropy, metrics=['accuracy'])
        _mod.fit(self.video_generator(batch_size = batch_size, train=True), epochs = epoch, steps_per_epoch = steps, validation_data = self.video_generator(batch_size = batch_size, train=False), validation_steps = step_val)
        if save:
          if not os.path.isdir(path):
            os.mkdir(path)
            _mod.save(path)
          else:
            _mod.save(path)
        return _mod


if __name__=='__main__':
    mod = softcut('/train', '/test', 1, 1, 16, (50, 48, 27, 3)).train(32, 5, 40, 15, True, '/model')
