# Original starter code posted by Matt@http://www.raspberrypi-spy.co.uk/
# Modifications ensued.
# Source: http://www.raspberrypi-spy.co.uk/2012/07/stepper-motor-control-in-python/

# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
from numpy import sqrt
 
#-----------------------------#
# Define Classes to be called #
#-----------------------------#

class Stepper:
  '''
  This class will drive bipolar stepper motors

  initiate by using stepper((pin1,pin2,pin3,pin4));
  the pins above are the GPIO pin number connected to the motor driver
  
  Usable pins on the raspberry Pi 2 B are: 2 - 27
  of which, 5,6,10,12,13,16,20,21,26 are GPIO only

  '''
  
  # Define drive sequences
  SeqHS   = [(1,0,0,0),
                  (1,1,0,0),
                  (0,1,0,0),
                  (0,1,1,0),
                  (0,0,1,0),
                  (0,0,1,1),
                  (0,0,0,1),
                  (1,0,0,1)]

  SeqFHT  = [(1,0,0,1),
                  (1,1,0,0),
                  (0,1,1,0),
                  (0,0,1,1)]

  SeqFLP  = [(1,0,0,0),
                  (0,1,0,0),
                  (0,0,1,0),
                  (0,0,0,1)]

  # Some global records keeping to prevent toe stepping
  legal_pins = (range(2,27))
  pins_in_use = []
  StepDir = 1 # 1 or -1

  # Stepper property constant(ish) definition
  STEPPER_RPM = 100
  STEP_PER_REV = 200
  STEP_WAIT_TIME = 3 #(millisecond)

  # Pick driving sequence (may inplement some kind of user input later)
  Seq = SeqHS
  HALF_STEP_ACTIVE = 1

  # Variable to keep tabs on the current driving state
  driving_seq_pos = 0

  def __init__(self,StepPins):
    '''
    This is the Initialization function for the class

    Note on the driving sequence:
    SeqHS is for driving the motor in half steps, with the highest resolution
    SeqFHT is for full step, high torque driving, engizes both phases when stepping
    SquFLP is for full step, low current driving, energize only one phase when stepping

    User may be permitted to pick their driving sequence based on the task required
    '''
    super(Stepper, self).__init__()

    # Use BCM GPIO references
    # instead of physical pin numbers
    GPIO.setmode(GPIO.BCM)

    # Set all pins as output
    for pin in StepPins:
      print "Setup pins"
      GPIO.setup(pin,GPIO.OUT)
      GPIO.output(pin, False)

    step_seq_size = len(self.Seq)-1
 
  def step(step_distance):
     
    for i in range(0,abs(step_distance))
      # If we reach the end of the sequence
      # start again
      if (StepCounter>=len(Seq)):
        StepCounter = 0
      elif (StepCounter<0):
        StepCounter = len(Seq)-1

      if(step_distance > 0): # If stepping forward
        StepCounter++
      if(step_distance < 0): # If stepping back
        StepCounter--

      #write operation to pins
      for pin in range(0, 4):
        xpin = StepPins[pin]
        if self.Seq[StepCounter][pin]!=0:
          GPIO.output(xpin, True)
        else:
          GPIO.output(xpin, False)

      # Wait apporiate wait time
      time.sleep(STEP_WAIT_TIME)

  def setRPM(new_rpm):
    ''' This function sets the speed of which the stepper is driven
    as of now this does not take into account the execution latencies
    will calibrate later once the prototype is functional

    setRPM(new_rpm)
    '''
    if (HALF_STEP_ACTIVE):
      STEP_WAIT_TIME = 1000/((new_rpm * STEP_PER_REV * 2)/60) #in miliseconds
    else:
      STEP_WAIT_TIME = 1000/((new_rpm * STEP_PER_REV)/60) #in miliseconds
    print("New step rate set, %d steps per second \n", int(1/STEP_WAIT_TIME))

  def setStepperRes(step_per_rev):
    ''' This function set the steps per revolution of the stepper motor
    input the step per rev in full stpes. (half stepping will be accounted for)

    setStepperRes(step_per_rev)
    '''
    STEP_PER_REV = step_per_rev
    print("New stepper resolution set, %d steps fer revolution \n", STEP_PER_REV)


  def stepperProperties(new_rpm,step_per_rev):
    ''' This function is basically combines self.stepPerRev and self.setRPM
    use for setting up the stepper prperties.

    stepperProperties(new_rpm,step_per_rev)
    '''

    self.setStepperRes(step_per_rev)
    self.setRPM(new_rpm)

  def setStepRate(step_rate):
    ''' This function allows you to set step rate of the stepper motor manually
        
    setStepRate(step_rate)
    '''
    STEP_WAIT_TIME = 1/step_rate
    print("New step rate set, %d steps per second \n", int(1/STEP_WAIT_TIME))

  def setFeedRate(dy,dx,feed_rate):
    ''' This function allows you to set the speed of the motor according to the feed rate of
    the material being cut

    setFeedRate(Setp_per_unit_X_distance, Setp_per_unit_Y_distance, Feed_rate_unit_distance_per_second)
    '''

    du = sqrt(dy^2+dx^2)
    if (du != 0):
      STEP_WAIT_TIME = 1/(feed_rate/du)
      print("New step rate set, %d steps per second \n", int(1/STEP_WAIT_TIME))
    else:
      print("Step rate NOT set, sqrt(dy^2+dx^2) == 0!")
