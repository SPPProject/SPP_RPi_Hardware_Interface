import sys
import time
import RPi.GPIO as GPIO
#import stepper as stepper
import serial
import os.path
import time, datetime
from numpy import pi, sin, cos, sqrt, arccos, arcsin


import Motor_control
from Bipolar_Stepper_Motor_Class import Bipolar_Stepper_Motor


################################################################################################
################################################################################################
#################                                ###############################################
#################    G code reading Functions    ###############################################
#################                                ###############################################
################################################################################################
################################################################################################

def XYposition(lines):
    #given a movement command line, return the X Y position
    xchar_loc=lines.index('X');
    i=xchar_loc+1;
    while (47<ord(lines[i])<58)|(lines[i]=='.')|(lines[i]=='-'):
        i+=1;
    x_pos=float(lines[xchar_loc+1:i]);    
    
    ychar_loc=lines.index('Y');
    i=ychar_loc+1;
    while (47<ord(lines[i])<58)|(lines[i]=='.')|(lines[i]=='-'):
        i+=1;
    y_pos=float(lines[ychar_loc+1:i]);    

    return x_pos,y_pos;

def IJposition(lines):
    #given a G02 or G03 movement command line, return the I J position
    ichar_loc=lines.index('I');
    i=ichar_loc+1;
    while (47<ord(lines[i])<58)|(lines[i]=='.')|(lines[i]=='-'):
        i+=1;
    i_pos=float(lines[ichar_loc+1:i]);    
    
    jchar_loc=lines.index('J');
    i=jchar_loc+1;
    while (47<ord(lines[i])<58)|(lines[i]=='.')|(lines[i]=='-'):
        i+=1;
    j_pos=float(lines[jchar_loc+1:i]);    

    return i_pos,j_pos;

def moveto(MX,x_pos,dx,MY,y_pos,dy,speed,engraving):
#Move to (x_pos,y_pos) (in real unit)
    stepx=int(round(x_pos/dx))-MX.position;
    stepy=int(round(y_pos/dy))-MY.position;

    Total_step=sqrt((stepx**2+stepy**2));
    
    if Total_step>0:
        if lines[0:3]=='G0 ': #fast movement
            print 'No Laser, fast movement: Dx=', stepx, '  Dy=', stepy;
            Motor_control.Motor_Step(MX,stepx,MY,stepy,50);
        else:
            print 'Laser on, movement: Dx=', stepx, '  Dy=', stepy;
            Motor_control.Motor_Step(MX,stepx,MY,stepy,speed);
    return 0;


################################################################################################
################################################################################################
#################                            ###################################################
#################    Parameters set up       ###################################################
#################                            ###################################################
################################################################################################
################################################################################################

# This will create a file and store recieved G-Code, records of all runs will be kept
# for debugging / logging purposes

dateString = '%Y-%m-%d - '
date_now = datetime.datetime.now().date().strftime(dateString)
log_number = 1

while True:
  print 'loop'
  filename = './Gcode_log/' + date_now + str(log_number) + '.nc'
  if os.path.exists(filename):
    # File already exist, advance number
    log_number += 1
  elif(log_number > 1000):
    # Incase things go kaput
    break
  else:
    # File of given name do not exist, create and use
    break
open(filename, 'a').close()

#filename = './reference_stuff/spiral.nc'

GPIO.setmode(GPIO.BCM)

#Define stepper motors:
MX = Bipolar_Stepper_Motor(23,22,24,26)
print("Initialized Motor 1 (X) with pin 5,6,10,12")
MY = Bipolar_Stepper_Motor(11,7,5,3)
print("Initialized Motor 2 (Y) with pin 13,16,20,21")

#####################################################
## TO BE DETERMINED ONCE MACHANICAL STUFF ARE DOWN ##
#####################################################
dx=0.075; #resolution in x direction. Unit: mm
dy=0.075; #resolution in y direction. Unit: mm
feed_rate = 0.01

# Currently set to be conservative, diagonal cut will not exceed feed rate
#MX.setFeedRate(dy,dx,feed_rate)
#MY.setFeedRate(dy,dx,feed_rate)

###########################################################################################
###########################################################################################
#################                           ###############################################
#################  Recieve and store Gcode  ###############################################
#################                           ###############################################
###########################################################################################
###########################################################################################

try: #try and handle interrupt gracefully
  port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.5)
  gcode = open(filename,'a')

  print("Waiting for Serial Input...")
  while True:
    ch = port.read()
    print("Serial Wait Loop")
    if (ch != ''):
      #Recieved not blank
      print("Recieving Gcode from Serial")
      gcode.write(ch)
      break

  while True:
    ch = port.read()
    print('.')
    if (ch == ''):
      #end of transmission reached
      break
    gcode.write(ch)

  #print("Gcode recieved and stored, starting cut in 5 seconds")
  #delay(5000);

  unused = input("Gcode recieved and stored, press enter to continue")

  gcode.close()
  port.close()


###########################################################################################
###########################################################################################
#################                           ###############################################
#################   Reading Stored Gcode    ###############################################
#################                           ###############################################
###########################################################################################
###########################################################################################


  for lines in open(filename,'r'):
    if lines==[]:
      1; #blank lines
    elif lines[0:3]=='G90':
      print 'start';
       
    elif lines[0:3]=='G20':# working in inch;
      dx/=25.4;
      dy/=25.4;
      print 'Working in inch';
         
    elif lines[0:3]=='G21':# working in mm;
      print 'Working in mm';  
       
    #elif lines[0:3]=='M05':
    #  GPIO.output(Laser_switch,False);
    # print 'Laser turned off';
      
    #elif lines[0:3]=='M03':
    #  GPIO.output(Laser_switch,True);
    #  print 'Laser turned on';

    elif lines[0:3]=='M02':
    # GPIO.output(Laser_switch,False);
      print 'finished. shuting down';
      break;
    elif (lines[0:3]=='G1F')|(lines[0:4]=='G1 F'):
      1;#do nothing
    elif (lines[0:3]=='G0 ')|(lines[0:3]=='G1 ')|(lines[0:3]=='G01'):#|(lines[0:3]=='G02')|(lines[0:3]=='G03'):
      #linear engraving movement
      if (lines[0:3]=='G0 '):
        engraving=False;
      else:
        engraving=True;
         
      [x_pos,y_pos]=XYposition(lines);
      moveto(MX,x_pos,dx,MY,y_pos,dy,speed,engraving);
       
    elif (lines[0:3]=='G02')|(lines[0:3]=='G03'): #circular interpolation
      old_x_pos=x_pos;
      old_y_pos=y_pos;

      [x_pos,y_pos]=XYposition(lines);
      [i_pos,j_pos]=IJposition(lines);

      xcenter=old_x_pos+i_pos;   #center of the circle for interpolation
      ycenter=old_y_pos+j_pos;
     
     
      Dx=x_pos-xcenter;
      Dy=y_pos-ycenter;      #vector [Dx,Dy] points from the circle center to the new position
     
      r=sqrt(i_pos**2+j_pos**2);   # radius of the circle
     
      e1=[-i_pos,-j_pos]; #pointing from center to current position
      if (lines[0:3]=='G02'): #clockwise
        e2=[e1[1],-e1[0]];      #perpendicular to e1. e2 and e1 forms x-y system (clockwise)
      else:                   #counterclock ise
        e2=[-e1[1],e1[0]];      #perpendicular to e1. e1 and e2 forms x-y system (counterclockwise)

      #[Dx,Dy]=e1*cos(theta)+e2*sin(theta), theta is the open angle

      costheta=(Dx*e1[0]+Dy*e1[1])/r**2;
      sintheta=(Dx*e2[0]+Dy*e2[1])/r**2;        #theta is the angule spanned by the circular interpolation curve
         
      if costheta>1:  # there will always be some numerical errors! Make sure abs(costheta)<=1
        costheta=1;
      elif costheta<-1:
        costheta=-1;

      theta=arccos(costheta);
      if sintheta<0:
        theta=2.0*pi-theta;

      no_step=int(round(r*theta/dx/5.0));   # number of point for the circular interpolation
     
      for i in range(1,no_step+1):
        tmp_theta=i*theta/no_step;
        tmp_x_pos=xcenter+e1[0]*cos(tmp_theta)+e2[0]*sin(tmp_theta);
        tmp_y_pos=ycenter+e1[1]*cos(tmp_theta)+e2[1]*sin(tmp_theta);
        moveto(MX,tmp_x_pos,dx,MY, tmp_y_pos,dy,speed,True);
     
except KeyboardInterrupt:
    print("Terminated by keyboard interrupt, good by")
 
#GPIO.output(Laser_switch,False);   # turn off laser
moveto(MX,0,dx,MY,0,dy,50,False);  # move back to Origin
 
MX.unhold();
MY.unhold();
 
GPIO.cleanup();