from __future__ import print_function
import caffe
import numpy as np
from caffe import layers as L, params as P, to_proto
from caffe.proto import caffe_pb2
import os
import h5py
from game_globals import *


class MinecraftNet:
    
    def __init__(self, model_filename=''):
        #caffe.set_mode_cpu()   #uncomment if no GPU
        self.solver = caffe.SGDSolver(REINFORCEMENT_PROTO)
               
        # Model already exists, then load it
        # Otherwise, save a new, random model
        if model_filename != '' and os.path.exists(model_filename):
            self.model_filename = model_filename
            self.load_model(self.model_filename)
        else:
            self.model_filename = REINFORCEMENT_MODEL
            self.solver.net.save(self.model_filename)      
        
    def load_model(self, path_to_model):
        #print ("loading model: ", path_to_model)
        self.solver.net.copy_from(path_to_model)
        
    def reload_net(self):
        self.solver = caffe.SGDSolver(REINFORCEMENT_PROTO)
        self.load_model(self.model_filename)
        #print("NETWORK PARAMS: %s" % str(self.solver.net.params['ip1'][0].data[...]))

    
    def train(self, itrs):
        self.reload_net()
        self.solver.step(itrs)
        self.solver.net.save(self.model_filename)
        
        
    def forward(self, data):
        #print("FORWARD DATA:", data)
        self.set_test_input_data(data)
        out = self.solver.test_nets[0].forward()
        # forward_input = self.solver.net.blobs['data'].data[...]
        #print("FORWARD INPUT:", self.solver.test_nets[0].blobs['data'].data[...])
        output_array = self.solver.test_nets[0].blobs['ip2'].data[...][0]  # HACK
        #print("OUTPUT:", output_array)
        return output_array


    def set_test_input_data(self, input_array):
        #print(input_array)
        input_array = np.array(input_array, dtype=np.float32)
        #input_array = input_array.reshape((WINDOW_SIZE, WINDOW_SIZE))
        #input_array = input_array[np.newaxis, np.newaxis, :, :]
        input_array = input_array[np.newaxis, np.newaxis, np.newaxis, :]

        #unused_labels = np.array([[[[1]*64]]], dtype=np.float32)
        #self.solver.net.set_input_arrays(input_array, unused_labels)
        #self.solver.test_nets[0].set_input_arrays(input_array, unused_labels)
        self.solver.test_nets[0].blobs['data'].data[...] = input_array
        #self.solver.net.blobs

    def set_train_input_data(self, orig_input, orig_labels):
        inputs = []
        for i in range(len(orig_input)):
            curr_input = np.array(orig_input[i].toCNNInput(), dtype=np.float32)
            #curr_input = curr_input.reshape((WINDOW_SIZE, WINDOW_SIZE))
            curr_input *= (1/255.)  # Scale separately so labels aren't scaled in Caffe
            #curr_input = np.append(curr_input, orig_labels[i])
            inputs.append(curr_input)

        labels = []
        for i in range(len(orig_labels)):
            labels.append(orig_labels[i])
            
        input_array = np.array(inputs, dtype=np.float32)
        input_array = input_array[:, np.newaxis, np.newaxis, :]

        label_array = np.array(labels, dtype=np.float32)
        label_array = label_array[:, np.newaxis, np.newaxis, :]

        # Write out the inputs and targets in hdf5 format
        hdf5_dataset_filename = 'datasets/tmp_training_dataset.hdf5'

        f = h5py.File(hdf5_dataset_filename, 'w')
        f.create_dataset('data', (TRAINING_BATCH_SIZE, 1, 1, FEATURE_VECTOR_SIZE), data=input_array, dtype='f8')
        f.create_dataset('label', (TRAINING_BATCH_SIZE, 1, 1, OUTPUT_VECTOR_SIZE), data=label_array, dtype='f8')
        f.close()
        

if __name__ == '__main__':
    mnet = MinecraftNet()
    #mnet.load_model('snapshots/minecraft/snapshots_iter_5.caffemodel')
    #mnet.train(5)
    
    
