#!/usr/bin/python2.7

# BCM 23

import RPi.GPIO as GPIO
#import time

# when using hackerspace door pihat
# in rs422 mode pin BCM 23 (board 16)
# is set high as we use it to tell the 
# transmit enable pin on the 
# transmit chip to always be in
# transmit mode

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.OUT)

GPIO.output(23, GPIO.HIGH)


#time.sleep(900)

