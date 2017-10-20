'''
self_driving.py
Created By: Peter Gish
Last Modified: 10/15/17

Main driver file for project.
Requirements:
    -opencv2
    -numpy
    -arduino (with known serial port)
    -raspberry pi (on same network with known ip address)

**Run collect_training_data.py & mlp_training.py prior to this program**

This program handles two threads:
    1)  distance_thread: (Port 8002)
            -handles sensor data from the raspberry pi
            -checks distance value against minimum value to determine if the car needs to stop
    2)  video_thread: (Port 8000)
            -handles video from the raspberry pi
            -collects frames and uses pre-trained mlp to predict action
'''

import threading
import socketserver
import serial
import cv2
import numpy as np

# distance data measured by ultrasonic sensor
sensor_data = " "


class SensorData(socketserver.BaseRequestHandler):
    data = " "

    def handle(self):
        global sensor_data
        try:
            while self.data:
                self.data = self.request.recv(1024)
                sensor_data = round(float(self.data), 1)
                print("sensor_data")
        finally:
            print("Connection closed on thread 2")


class NeuralNetwork(object):

    def __init__(self):
        self.model = cv2.ml.ANN_MLP_create()

    # create new network, load data from mlp.xml training data
    def create(self):
        layer_size = np.int32([38400, 32, 4])
        self.model.setLayerSizes(layer_size)
        self.model.load('neural_net/mlp_xml/mlp.xml')

    def predict(self, samples):
        retvals, outputs = self.model.predict(samples)
        return outputs.argmax(-1)

class CarControl(object):

    # serial port of arduino, baudrate 115200
    def __init__(self):
        self.serial_port = serial.Serial('/dev/cu.usbserial-A900cfFq', 115200, timeout=1)

    def stop(self):
        self.serial_port.write(chr(0))

    def control(self, command):
        if command == 2:
            self.serial_port.write(chr(1))
            print("Forward")
        elif command == 0:
            self.serial_port.write(chr(4))
            print("Left")
        elif command == 1:
            self.serial_port.write(chr(3))
            print("Right")
        elif command == 3:
            print("Braking")
            self.serial_port.write(chr(5))
        else:
            self.stop()


class VideoStream(socketserver.StreamRequestHandler):
    model = NeuralNetwork()
    model.create()

    rc_car = CarControl()

    def handle(self):
        global sensor_data
        stream_bytes = ' '
        # read in frames
        try:
            while True:
                stream_bytes += self.rfile.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    # lower half of the image
                    half_gray = gray[120:240, :]

                    # Display the resulting frame
                    cv2.imshow('frame', image)

                    # reshape image
                    image_array = half_gray.reshape(1, 38400).astype(np.float32)

                    # neural network makes prediction
                    prediction = self.model.predict(image_array)

                    # stop conditions
                    if sensor_data is not None and sensor_data < 30:
                        print("Stopping- object")
                        self.rc_car.stop()

                    else:
                        self.rc_car.control(prediction)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.rc_car.stop()
                        break
            cv2.destroyAllWindows()
        finally:
            print("Thread 1 closed")


# initialize the TCP server & begin thread for video and distance
class ThreadServer(object):

    def server_thread(self, port):
        server = socketserver.TCPServer((self, port), VideoStream)
        server.serve_forever()

    def server_thread2(self, port):
        server = socketserver.TCPServer((self, port), SensorData)
        server.serve_forever()

    # ip address of pi
    distance_thread = threading.Thread(target=server_thread2, args=('172.31.2.94', 8002))
    distance_thread.start()
    video_thread = threading.Thread(target=server_thread('172.31.2.94', 8000))
    video_thread.start()


if __name__ == '__main__':
    ThreadServer()
