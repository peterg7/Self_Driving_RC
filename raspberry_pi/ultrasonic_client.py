'''
ultrasonic_client.py
Created By: Peter Gish
Last Modified: 10/14/17

**Must be running on pi
client program for sensor-data host on computer
'''

from socket import *
import time
import RPi.GPIO as GPIO

# define pi GPIO
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# referring to the pins by GPIO numbers
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# output pin: Trigger
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
# input pin: Echo
GPIO.setup(GPIO_ECHO,GPIO.IN)
# initialize trigger pin to low
GPIO.output(GPIO_TRIGGER, False)

# create a socket and bind socket to the host, ip address of computer, port 8002
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(('192.168.1.100', 8002))


def measure():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    elapsed = stop-start
    return (elapsed*34300)/2


try:
    while True:
        distance = measure()
        print "Distance : %.1f cm" % distance
        # send data to the host every 0.5 sec
        client_socket.send(str(distance))
        time.sleep(0.5)
finally:
    client_socket.close()
    GPIO.cleanup()
