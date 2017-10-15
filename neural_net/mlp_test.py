'''
mlp_predict_test.py
Created By: Peter Gish
Last Modified: 10/14/17
uses training data in 'testing_data/*.npz'
creates mlp and loads previously set params
'''
import cv2
import numpy as np
import glob


# load training data
image_array = np.zeros((1, 38400))
label_array = np.zeros((1, 4), 'float')
training_data = glob.glob('testing_data/*.npz')

for single_npz in training_data:
    with np.load(single_npz) as data:
        print data.files
        test_temp = data['train']
        test_labels_temp = data['train_labels']
        print test_temp.shape
        print test_labels_temp.shape
    image_array = np.vstack((image_array, test_temp))
    label_array = np.vstack((label_array, test_labels_temp))

test = image_array[1:, :]
test_labels = label_array[1:, :]
print test.shape
print test_labels.shape

# create mlp
layer_sizes = np.int32([38400, 32, 4])
model = cv2.ANN_MLP()
model.create(layer_sizes)
model.load('mlp_xml/mlp.xml')

# generate predictions
t0 = cv2.getTickCount()
retvals, outputs = model.predict(test)
prediction = resp.argmax(-1)
t1 = cv2.getTickCount()
time = (t1 - t0)/cv2.getTickFrequency()

print 'Prediction:', prediction

true_labels = test_labels.argmax(-1)
print 'True labels:', true_labels

num_correct = np.sum(true_labels, prediction)
print(num_correct)
test_rate = np.mean(prediction, true_labels)
print 'Test rate: ', (test_rate*100)
