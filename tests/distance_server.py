'''
distance_server.py
Created By: Peter Gish
Last Modified: 10/13/17
establishes TCP connection with raspberry pi
on same network. streams in data from ultrasonic
sensor once the connection is established
'''

import socket
import time


class SensorStreamingTest(object):
    def __init__(self):
        self.server_socket = socket.socket()
        # ip address of pi
        self.server_socket.bind(('172.31.3.57', 8002))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.streaming()

    def streaming(self):
        try:
            print "Connection from: ", self.client_address
            start = time.time()

            while True:
                sensor_data = float(self.connection.recv(1024))
                print "Distance: %0.1f cm" % sensor_data

                # testing for 10 seconds
                if time.time() - start > 30:
                    break
        finally:
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    SensorStreamingTest()
