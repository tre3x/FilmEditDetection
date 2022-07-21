import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import cv2
import argparse
import numpy as np
import tensorflow as tf
from hardcut_data import hardcut_data
import tensorflow.keras.applications as kerasApp
from tensorflow.keras.layers import AveragePooling2D, Dense, Flatten

class hardcut():
    def __init__(self, train_path, test_path, encoder, weights, dim):
        self.train_path = train_path
        self.test_path = test_path
        self.encoder = encoder
        self.weights = weights
        self.dim = dim

    def get_data(self):
        train_data, test_data = hardcut_data(self.train_path, self.test_path).run()
        return np.array(train_data), np.array(test_data)

    def get_model(self):
        if self.encoder=='VGG16':
            model = kerasApp.VGG16(input_shape=self.dim, include_top=False, weights=self.weights)
            model_clone = kerasApp.VGG16(input_shape=self.dim, include_top=False, weights=self.weights)
        if self.encoder=='ResNet50':
            model = kerasApp.ResNet50(input_shape=self.dim, include_top=False, weights=self.weights)
            model_clone = kerasApp.ResNet50(input_shape=self.dim, include_top=False, weights=self.weights)
        for layer in model_clone.layers:
            layer._name = layer._name+'_'
        output = model.layers[-1].output
        output_clone = model_clone.layers[-1].output
        output = AveragePooling2D()(output)
        output_clone = AveragePooling2D()(output_clone)
        output = tf.keras.layers.Flatten()(output)
        output_clone = tf.keras.layers.Flatten()(output_clone)
        fused = tf.keras.layers.Concatenate(axis = 1)([output, output_clone])
        layer = tf.keras.layers.Dense(4096)(fused)
        layer = tf.keras.layers.Dense(1024)(layer)
        layer = tf.keras.layers.Dense(512)(layer)
        layer = tf.keras.layers.Dense(64)(layer)
        layer = tf.keras.layers.Dense(2, activation = 'softmax')(layer)
        model = tf.keras.Model(inputs=[model.input, model_clone.input], outputs=layer)
        return model

    def read_frames(self, path):
        frame1 = cv2.imread(os.path.join(path, "1.png"))
        frame1 = cv2.resize(frame1, (self.dim[0], self.dim[1]))
        frame2 = cv2.imread(os.path.join(path, "2.png"))
        frame2 = cv2.resize(frame2, (self.dim[0], self.dim[1]))
        return frame1, frame2

    def image_generator(self, batch_size, train):
        while True:
            if train:
                data, _ = self.get_data()
            else:
                _, data = self.get_data()
            batch = data[np.random.choice(data.shape[0], batch_size, replace=False)]
            batch_x1 = []
            batch_x2 = []
            batch_output = []
            
            for elem in batch:
                x1, x2 = self.read_frames(elem[0])
                output = elem[1]
                batch_x1.append(x1)
                batch_x2.append(x2)
                batch_output.append(output)
            batch_x1 = np.array(batch_x1)
            batch_x2 = np.array(batch_x2)
            batch_y = np.array(batch_output)
            yield [batch_x1, batch_x2], batch_y

    def train(self, batch_size, epoch, steps, step_val, save=False, checkpoint_filepath='/'):
        if save:
          if not os.path.isdir(checkpoint_filepath):
            os.mkdir(checkpoint_filepath)
        _mod = self.get_model()
        _mod.compile('Adam', loss = tf.keras.losses.categorical_crossentropy, metrics=['accuracy'])
        model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_filepath, save_best_only=True, save_weights_only=False, monitor='val_accuracy', mode='max')
        _mod.fit(self.image_generator(batch_size = batch_size, train=True), epochs = epoch, steps_per_epoch = steps, validation_data = self.image_generator(batch_size = batch_size, train=False), validation_steps = step_val, callbacks=[model_checkpoint_callback])
        return _mod


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='3DCNN training Tool')

    parser.add_argument('--trainpath', type=str, default='', help='What is the training video path?')
    parser.add_argument('--testpath', type=str, default='', help='What is the testing 3DCNN model?')
    parser.add_argument('--encoder', type=str, default=-1, help='What is the encoder (VGG-16, ResNet-50)?')
    parser.add_argument('--weights', type=str, default=-1, help='What is the pretrained weights to be used?')
    parser.add_argument('--dim', type=int, default=-1, help='What is the input dimension?')

    parser.add_argument('--batch', type=int, default=-1, help='What is the batchsize for training?')
    parser.add_argument('--epoch', type=int, default=-1, help='What is the epoch for training?')
    parser.add_argument('--steps', type=int, default=-1, help='What is the steps per epoch for training?')
    parser.add_argument('--stepsval', type=int, default=-1, help='What is the steps per epoch for validation?')
    parser.add_argument('--modpath', type=str, default=-1, help='What is the path of saved model?')

    args = parser.parse_args()
    print("Configuration")
    print("----------------------------------------------------------------------")
    print("Training Video path : {}".format(args.trainpath))
    print("Testing video path : {}".format(args.testpath))
    print("Encoder used : {}".format(args.encoder))
    print("Input Image dimension : {}".format((args.dim, args.dim, 3)))
    print("Batch size : {}".format(args.batch))
    print("Number of epochs for training : {}".format(args.epoch))
    print("Number of steps per epoch while training : {}".format(args.steps))
    print("Number of steps per epoch while validation : {}".format(args.stepsval))
    print("Trained Model path : {}".format(args.modpath))
    print("----------------------------------------------------------------------")


    mod = hardcut(args.trainpath, args.testpath, args.encoder, args.weights, (args.dim, args.dim, 3)).train(args.batch, args.epoch, args.steps, args.stepsval, True, args.modpath)
