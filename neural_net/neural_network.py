'''
neural_net.py
Created By: Peter Gish
Last Modified: 4/10/15
small scale neural network (3 input neurons, 4 hidden neurons, 1 output)
network is trained to predict y given x
'''

import numpy as np


# activate a neuron
def nonlin(xin, deriv=False):
    if deriv:
        return xin * (1 - xin)
    return 1 / (1 + np.exp(-xin))


x = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
y = np.array([[0, 1, 1, 0]]).T

np.random.seed(1)

# randomly initialize weights with mean 0
s0 = 2 * np.random.random((3, 4)) - 1
s1 = 2 * np.random.random((4, 1)) - 1

# trains network using back propagation
for j in xrange(60000):
    # Feed forward through layers 0, 1, and 2
    l0 = x
    l1 = nonlin(np.dot(l0, s0))
    l2 = nonlin(np.dot(l1, s1))
    l2_error = y - l2

    if (j % 10000) == 0:
        print "Error: " + '%.8f' % np.mean(np.abs(l2_error))

    # calculate change in l2
    l2_d = l2_error*nonlin(l2, deriv=True)

    # l1 impact on l2 error
    l1_error = l2_d.dot(s1.T)

    # calculate change in l1
    l1_d = l1_error * nonlin(l1, deriv=True)

    # adjust weights
    s1 += l1.T.dot(l2_d)
    s0 += l0.T.dot(l1_d)

# output final predictions
np.set_printoptions(precision=5)
print "Output After Training:"
print l2
