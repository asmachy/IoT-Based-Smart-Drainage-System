import RPi.GPIO as GPIO
import time
from time import sleep
import pigpio
from urllib.request import urlopen
import sys
import random

#mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
 
location = 2

fromaddr = "asmathesispurpose@gmail.com"
toaddr = "asmachycu15@gmail.com"

mail = MIMEMultipart()
 
mail['From'] = fromaddr
mail['To'] = toaddr
mail['Subject'] = "Alert"
body = "Water-logging found at Point:"+str(location)

sum_flow = 0
sum_dist = 0

avg_flow = 0
avg_dist = 0

waterflow = 0
distance = 0

data = "Water-logging found"


flowGpio = 4

#upload
import http.client, urllib
#sleep = 60 # how many seconds to sleep between posts to the channel
key = 'YJ6FQCDAJSXWUFMJ'  # Thingspeak channel to update
BASE_URL = "https://api.thingspeak.com/update?api_key={}".format(key)
thingspeakPrevSec = 0
thingspeakInterval = 5

#ultrasonic sensor

GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 23                                  #Associate pin 23 to TRIG
ECHO = 24                                  #Associate pin 24 to ECHO

intervalTime  = 1  # in seconds
old_count = 0

print ("Distance and WaterFlow measurement in progress")

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

datacount = 0
falsedata = 0       

timecountdist = 0
timecountflow = 0

def sendMail(data):
  mail.attach(MIMEText(body, 'plain'))
  print (data)
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.ehlo()
  server.starttls()
  server.login(fromaddr, "43asma43")
  text = mail.as_string()
  server.sendmail(fromaddr, toaddr, text)
  server.close()
  
###################
  
def uploadAvgMeanValue(waterflow, distance, avg_flow, avg_dist):
    thingspeakHttp = BASE_URL + "&field1={:d}/s&field2={:.2f}cm&field3={:.2f}/s&field4={:.2f}cm".format(waterflow, distance, avg_flow, avg_dist)
    print (thingspeakHttp)
    
    try:
        conn = urlopen(thingspeakHttp)
        print("Response: {}".format(conn.read()))
        conn.close()
    except:
        print ("connection failed")

##########
  
while timecountdist <= 5 and timecountflow <= 5 :
    pi = pigpio.pi()
    old_count = 0
    pi.set_mode(flowGpio, pigpio.INPUT)
    pi.set_pull_up_down(flowGpio, pigpio.PUD_DOWN)

    flowCallback = pi.callback(flowGpio, pigpio.FALLING_EDGE)
    time.sleep(intervalTime)

    count = flowCallback.tally()
    waterflow = (count - old_count)
    print(waterflow)
    old_count = count
    
    GPIO.output(TRIG, False)                 #Set TRIG as LOW
    print ("Waitng For Sensor To Settle")
    time.sleep(2)                            #Delay of 2 seconds

    GPIO.output(TRIG, True)                  #Set TRIG as HIGH
    time.sleep(0.00001)                      #Delay of 0.0001 seconds
    GPIO.output(TRIG, False)                 #Set TRIG as LOW
 
    while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
        pulse_start = time.time()              #Saves the last known time of LOW pulse

    while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
        pulse_end = time.time()                #Saves the last known time of HIGH pulse 

    pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
    distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
    distance = round(distance, 2)            #Round to two decimal points
    distance = distance - 0.5
    
    datacount = datacount + 1
    if distance >= 300 or distance <= 1.2 :
        falsedata = falsedata + 1
        continue
    timecountdist = timecountdist + 1
    datacount = datacount + 1
    sum_dist = sum_dist + distance
    print ("waterflow: ",waterflow)
    print ("Distance: ",distance,"cm")
        
    timecountflow = timecountflow + 1
    sum_flow = sum_flow + waterflow
        
    if distance >= 20 :
        print("Safe Distance from water!")
    elif distance >= 15 and distance < 20 :
        print("Warning! Distance is low!")
    elif distance < 15 :
        print ("Danger! Danger! Sending mail...")
        try:
            data = "Water-logging found"
            body = "Water-logging found at Point:"+str(location)
            sendMail(data)
        except:
            print("Check Internet connection")
    
avg_dist = sum_dist/5
avg_flow = sum_flow/5
sum_dist = 0
sum_flow = 0

while True:
    try:
        pi = pigpio.pi()
        old_count = 0
        pi.set_mode(flowGpio, pigpio.INPUT)
        pi.set_pull_up_down(flowGpio, pigpio.PUD_DOWN)
    
        flowCallback = pi.callback(flowGpio, pigpio.FALLING_EDGE)
        time.sleep(intervalTime)

        count = flowCallback.tally()
        waterflow = (count - old_count)
        old_count = count
        
        ###############
        
        GPIO.output(TRIG, False)                 #Set TRIG as LOW
        print ("Waitng For Sensor To Settle")
        time.sleep(2)                            #Delay of 2 seconds
    
        GPIO.output(TRIG, True)                  #Set TRIG as HIGH
        time.sleep(0.00001)                      #Delay of 0.0001 seconds
        GPIO.output(TRIG, False)                 #Set TRIG as LOW
     
        while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
            pulse_start = time.time()              #Saves the last known time of LOW pulse
    
        while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
            pulse_end = time.time()                #Saves the last known time of HIGH pulse 
    
        pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
        distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
        distance = round(distance, 2)            #Round to two decimal points
        distance = distance - 0.5
    
        ####################
        
        datacount = datacount + 1
        if avg_dist - distance > 200 or distance - avg_dist > 200 or distance >= 300 :
            falsedata = falsedata + 1
            continue
        datacount = datacount + 1
        timecountdist = timecountdist + 1
        sum_dist = sum_dist + distance
            
        timecountflow = timecountflow + 1
            
        print ("waterflow: ",waterflow)
        print ("Distance: ",distance,"cm")
        
        if avg_flow - waterflow >= 10 and avg_dist - distance >= 5 :
            print ("Warning! Warning! Blockage is detected!")
            print("Blockage is found between location ",location-1," and location ",location,"!")
        if distance >= 20 :
            print("Safe Distance from water!")
        elif distance >= 15 and distance < 20 :
            print("Warning! Distance is low!")
        elif distance < 15 :
            print ("Danger! Danger! Sending mail...")
            try:
                body = "Water-logging found at Point:"+str(location)
                sendMail(data)
            except:
                print("Check Internet connection")
        sum_flow = sum_flow + waterflow
        
        if timecountdist == 5 :
            avg_dist =  sum_dist/5
            sum_dist = 0
            print("Average Distance is: ",avg_dist)
        if timecountflow == 5 :
            avg_flow=  sum_flow/5
            sum_flow = 0
            print("Average water flow is: ", avg_flow)
        
        uploadAvgMeanValue(waterflow, distance, avg_flow, avg_dist)
    
    except KeyboardInterrupt:
        
        print ('\ncaught keyboard interrupt!')
        accuracy = ( (datacount - falsedata) * 100) / datacount
        accuracy = round(accuracy, 2)
        print("Measurement Accuracy: ", accuracy, "% .")
        GPIO.cleanup()
        sys.exit()