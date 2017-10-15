'''
collect_training_data.py
Created By: Peter Gish
Last Modified: 10/15/17
Requirements:
    -opencv2
    -pygame
    -numpy

listens to user input while recording images
pairs user action with image to use as training data for
neural net. stores training data in "training_data/test01.npz"
'''

import serial
import pygame
import socket
import numpy as np
import cv2


class CollectTrainingData(object):
    def __init__(self):
        # ip address of pi, use port 8000
        self.server_socket = socket.socket()
        self.server_socket.bind(('172.31.2.94', 8000))
        self.server_socket.listen(0)

        # accept a single connection (video stream from pi)
        self.connection = self.server_socket.accept()[0].makefile('rb')

        # connect to arduino serial port, baudrate = 115200
        self.ser = serial.Serial("/dev/cu.usbserial-A900cfFq", 115200, timeout=1)
        self.send_inst = True

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        pygame.init()
        self.collect_image()

    def collect_image(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print 'Collecting images'
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        # stream video frames one by one
        try:
            stream_bytes = ' '
            frame = 1
            while self.send_inst:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    lower = image[120:240, :]

                    # save streamed images
                    cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), image)
                    cv2.imshow('image', image)

                    # reshape the lower image into one row array
                    temp_array = lower.reshape(1, 38400).astype(np.float32)

                    frame += 1
                    total_frame += 1

                    # get usr_input from human driver
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            usr_input = pygame.key.get_pressed()

                            if usr_input[pygame.K_UP] and usr_input[pygame.K_RIGHT]:
                                print("Forward Right")
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[1]))
                                saved_frame += 1
                                self.ser.write(chr(6))

                            elif usr_input[pygame.K_UP] and usr_input[pygame.K_LEFT]:
                                print("Forward Left")
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[0]))
                                saved_frame += 1
                                self.ser.write(chr(7))

                            elif usr_input[pygame.K_DOWN] and usr_input[pygame.K_RIGHT]:
                                print("Reverse Right")
                                self.ser.write(chr(8))

                            elif usr_input[pygame.K_DOWN] and usr_input[pygame.K_LEFT]:
                                print("Reverse Left")
                                self.ser.write(chr(9))

                            # simple orders
                            elif usr_input[pygame.K_UP]:
                                print("Forward")
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[2]))
                                self.ser.write(chr(1))

                            elif usr_input[pygame.K_DOWN]:
                                print("Reverse")
                                saved_frame += 1
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[3]))
                                self.ser.write(chr(2))

                            elif usr_input[pygame.K_RIGHT]:
                                print("Right")
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[1]))
                                saved_frame += 1
                                self.ser.write(chr(3))

                            elif usr_input[pygame.K_LEFT]:
                                print("Left")
                                image_array = np.vstack((image_array, temp_array))
                                label_array = np.vstack((label_array, self.k[0]))
                                saved_frame += 1
                                self.ser.write(chr(4))

                            elif usr_input[pygame.K_x] or usr_input[pygame.K_q]:
                                print 'exit'
                                self.send_inst = False
                                self.ser.write(chr(0))
                                break

                        elif event.type == pygame.KEYUP:
                            self.ser.write(chr(0))

            # save training images and labels
            train = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            np.savez('training_data/test01.npz', train=train, train_labels=train_labels)

            e2 = cv2.getTickCount()
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print 'Streaming duration:', time0

        finally:
            print 'Finished data acquisition'
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    CollectTrainingData()
