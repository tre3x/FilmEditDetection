import os
import numpy as np
import tensorflow as tf

class model():
    '''
    This class contains the architecture of soft cut detector deep learning model.
    The architecture is basically of satcked dilated 3D CNN model to capture different 
    temporal features of a video snippet.
    INPUT : SDDCNN, DDCNN, F, inputdim
    SDDCNN-number of stacked dilated CNN blocks
    DDCNN-number of dilated CNN blocks
    F-number of filters/channels to be produced by convnets
    inputdim:Input dimension of series of frames of the video. Dimension-(framenumber, height, width, channel)
    OUTPUT -_model
    _model-final model to be trained

    To call this model :  model(SDDCNN, DDCNN, F).call(inputdim)
    '''
    def __init__(self, SDDCNN, DDCNN, F):
        self.DDCNN = DDCNN
        self.SDDCNN = SDDCNN
        self.F = F

    def CNN_3D(self, filter, kernel, dilation):
        '''
        Function to add 3D convolutional layers
        INPUT : filter, kernel, dilation
        filter-number of filters/channels to be produced by convnets
        kernel-knernel size of convnets
        dilation-dilation of convnets
        OUTPUT : conv
        conv-3D convolutional layer
        '''
        conv = tf.keras.layers.Conv3D(filters=filter, kernel_size=kernel, dilation_rate=dilation, padding="SAME", activation=tf.nn.relu, use_bias=True)
        return conv

    def DDCNN_blocks(self, input, filter):
        '''
        Function to add dilated deep convolutional layer blocks.
        Each block contains serveral convnets stacked in parallel followed by an average layer.
        INPUT : input, filter
        input-Input layer to DDCNN blocks
        filter-number of filters/channels to be produced by convnets
        OUTPUT : x
        x-final layer of DDCNN blocks 
        '''
        x = input
        for block in range(self.DDCNN):
            conv1 = self.CNN_3D(filter=filter, kernel=3, dilation=(1,1,1)) (x)
            conv2 = self.CNN_3D(filter=filter, kernel=3, dilation=(2,1,1)) (x)
            conv3 = self.CNN_3D(filter=filter, kernel=3, dilation=(4,1,1)) (x)
            conv4 = self.CNN_3D(filter=filter, kernel=3, dilation=(8,1,1)) (x)
            x = tf.keras.layers.Average()([conv1, conv2, conv3, conv4])
        return x

    def SDDCNN_blocks(self, input):
        '''
        Function to add stacked DDCNN blocks on top of one another.
        Each SDDCNN blocks contains numerous DDCNN blocks followed by 3D maxpool operation
        Input : input
        input-Input layer of the model
        OUTPUT : x
        x-output of SDDCNN blocks
        '''
        x = input
        for block in range(self.SDDCNN):
            filter = self.F*(2**block)
            x = self.DDCNN_blocks(x, filter)
            x = tf.keras.layers.MaxPool3D(pool_size=(2,2,2))(x)
        return x

    def fclayer(self, input, nodeconfig):
        '''
        Function to add the final fc layer which basically acts as a decoder of the model.
        INPUT : input, nodeconfig
        input-input to the fclayer from flattened output of SDDCNN blocks 
        nodeconfig-list of integers depicting number of nodes in each dense layer of the decoder
        OUTPUT : fc
        fc-output of fc layer stating the probabilities of cuts
        '''
        fc = input
        fc = tf.keras.layers.Dropout(0.5)(fc)
        for node in nodeconfig:
            fc = tf.keras.layers.Dense(node, activation=tf.nn.relu)(fc)
        fc = tf.keras.layers.Dense(3, activation=tf.nn.softmax)(fc)
        return fc

    def architecture(self, input):
        '''
        Function depicting the architectuire of the model
        INPUT : input
        input:Input layer of the model
        OUTPUT : out
        out-Output layer of the model
        '''
        out = self.SDDCNN_blocks(input)
        out = tf.keras.layers.Flatten()(out)
        out = self.fclayer(out, [1000, 100])
        return out

    def call(self, inputdim):
        '''
        Driver function to call the architecture of the model
        INPUT : inputdim
        inputdim-Input dimension of series of frames of the video. Dimension-(framenumber, height, width, channel)
        OUTPUT : _model
        _model-Final model
        '''
        input = tf.keras.Input(shape = inputdim)
        output = self.architecture(input)
        _model = tf.keras.Model(inputs=input, outputs=output)
        return _model

if __name__=='__main__':
    mod = model(1, 1, 16).call((50, 48, 27, 3))  
    print(mod.summary())