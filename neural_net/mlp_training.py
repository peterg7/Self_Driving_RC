'''
mlp_training.py
Created By: Peter Gish
Last Modified: 5/24/15
loads training data from "training_data/*.npz"
trains mlp and saves weights to "mlp_xml/mlp.xml"
'''

import cv2
import numpy as np
import glob

t0 = cv2.getTickCount()

# load training data
image_array = np.zeros((1, 38400))
label_array = np.zeros((1, 4), 'float')
training_data = glob.glob('training_data/*.npz')

for single_npz in training_data:
    with np.load(single_npz) as data:
        print data.files
        train_temp = data['train']
        train_labels_temp = data['train_labels']
    image_array = np.vstack((image_array, train_temp))
    label_array = np.vstack((label_array, train_labels_temp))

train = image_array[1:, :]
train_labels = label_array[1:, :]
print train.shape
print train_labels.shape

t00 = cv2.getTickCount()
image_time = (t00 - t0) / cv2.getTickFrequency()
print 'Loading image duration:', image_time

# set start time
t1 = cv2.getTickCount()

# create mlp
layer_sizes = np.int32([38400, 32, 4])
model = cv2.ml.ANN_MLP()
model.create(layer_sizes)
criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001)
criteria2 = (cv2.TERM_CRITERIA_COUNT, 100, 0.001)
params = dict(term_crit=criteria, train_method=cv2.ANN_MLP_TRAIN_PARAMS_BACKPROP,
              bp_dw_scale=0.001, bp_moment_scale=0.0)

print 'Training mlp'
num_iter = model.train(train, train_labels, None, params=params)

# set end time
t11 = cv2.getTickCount()
train_time = (t11 - t1)/cv2.getTickFrequency()

# save param
model.save('mlp_xml/mlp.xml')

print 'Ran for %d iterations' % num_iter

# create predictions
retvals, outputs = model.predict(train)
prediction = outputs.argmax(-1)
print 'Prediction:', prediction

train_rate = np.mean(prediction, training_data)
print 'Train rate:', (train_rate*100)
