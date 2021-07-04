import os
import glob
import numpy as np
import random


class softcut_data():
    '''
    DATA PIPELINE
    RETURNS VIDEO DATA PATHS WITH LABEL
    To load train data - softcut().load_traindata(train_path)
    To load test data - softcut().load_testdata(test_path)
    train_path:directory path of training video files
    test_path:directory path of test video files
    '''
    def get_dirname(self, path):
        '''
        GET CLASS NAMES
        INPUT : path
        path-directory path of target videos files. video files should be in directories according to class name.
        OUTPUT : dirname
        dirname-list of class names
        '''
        dirname = os.listdir(path)
        dirname = sorted(dirname)
        return dirname

    def get_labels(self, path, dirname):
        '''
        GET CLASS LABELS FOR TRAINING/TESTING OF THE DL MODEL
        INPUT : path, dirname
        path-directory path of target videos files. video files should be in directories according to class name.
        dirname-list of class names
        OUTPUT : label
        label-class labels
        '''
        img_id = path.split('/')[-2]
        label = []
        for dir in dirname:
            if dir == img_id:
                label.append(1)
            else:
                label.append(0)
        return label     

    def get_results(self, path, dirname):
        '''
        RETURNS VIDEO FILE PATHS WITH VIDEO CLASS LABEL
        INPUT : path, dirname
        path-directory path of target videos files. video files should be in directories according to class name.
        dirname-list of class names
        OUTPUT : results
        results-video file paths with video class label
        '''
        results = []
        for x in os.walk(path):
            for y in glob.glob(os.path.join(x[0], '*.avi')):
                label = np.array(self.get_labels(y, dirname))
                results.append([y, label])
        return results 

    def load_traindata(self, train_path):
        '''
        DRIVER FUNCTION TO RETURN TRAINING VIDEO FILE PATHS WITH VIDEO CLASS LABEL
        INPUT : train_path
        train_path:directory path of training video files
        OUTPUT : train_results
        train_results-training video file paths with video class label
        '''
        dir_name = self.get_dirname(train_path)
        train_results = np.array(self.get_results(train_path, dir_name), dtype=object)
        
        return train_results

    def load_testdata(self, test_path):
        '''
        DRIVER FUNCTION TO RETURN TEST VIDEO FILE PATHS WITH VIDEO CLASS LABEL
        INPUT : test_path
        test_path:directory path of test video files
        OUTPUT : test_results
        test_results-test video file paths with video class label
        '''
        dir_name = self.get_dirname(test_path)
        test_results = np.array(self.get_results(test_path, dir_name), dtype=object)
        
        return test_results


if __name__=='__main__':
    res = softcut().load_traindata('/train')
    res = softcut().load_testdata('/test')
    print(res[np.random.choice(res.shape[0], 32, replace=False), :])
    