# Original starter code posted by Matt@http://www.raspberrypi-spy.co.uk/
# Modifications ensued.
# Source: http://www.raspberrypi-spy.co.uk/2012/07/stepper-motor-control-in-python/


#!/usr/bin/env python


# Some global records keeping to prevent toe stepping
legal_pins = ()
pins_in_use = []


# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
 
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
 
# Define GPIO signals to use
# Physical pins 11,15,16,18
# GPIO17,GPIO22,GPIO23,GPIO24
StepPins = [17,22,23,24]
 
# Set all pins as output
for pin in StepPins:
  print "Setup pins"
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)
 



#-----------------------------#
# Define Classes to be called #
#-----------------------------#

class stepper(object):
  '''
  This class will drive bipolar stepper motors

  initiate by using stepper(pin1,pin2,pin3,pin4);
  the pins above are the number 

  '''

  def __init__(self,pin1,pin2,pin3,pin4):
    # Define advanced sequence
    # as shown in manufacturers datasheet
    self.Seq = [(1,0,0,0),
                (1,1,0,0),
                (0,1,0,0),
                (0,1,1,0),
                (0,0,1,0),
                (0,0,1,1),
                (0,0,0,1),
                (1,0,0,1)]


StepCount = len(Seq)-1
StepDir = 2 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise
 
# Read wait time from command line
if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(1000)
else:
  WaitTime = 10/float(1000)
 
# Initialise variables
StepCounter = 0
 
# Start main loop
while True:
 
  for pin in range(0, 4):
    xpin = StepPins[pin]print StepCounter
    print pin
    if Seq[StepCounter][pin]!=0:
      print " Step %i Enable %i" %(StepCounter,xpin)
      GPIO.output(xpin, True)
    else:
      GPIO.output(xpin, False)
 
  StepCounter += StepDir
 
  # If we reach the end of the sequence
  # start again
  if (StepCounter>=StepCount):
    StepCounter = 0
  if (StepCounter<0):
    StepCounter = StepCount
 
  # Wait before moving on
  time.sleep(WaitTime)