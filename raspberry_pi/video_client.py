'''
stream_client.py
Created By: Peter Gish
Last Modified: 10/14/17

**Must be running on raspberry pi
client program for video stream host on computer
'''
import io
import socket
import struct
import time
import picamera

# create socket and bind host, ip address of computer, port 8000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.100', 8000))
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
        # pi camera resolution
        camera.resolution = (320, 240)
        # 10 frames/sec
        camera.framerate = 10
        time.sleep(2)
        start = time.time()
        stream = io.BytesIO()

        # send jpeg format video stream
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > 600:
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
