import math
import time
import RPi.GPIO as GPIO
import dht11
import wiringpi as w
import slackweb
from config_csv import ConfigJson as CJ
DIVR = 10000 # 4.7k ohm
THERMISTOR =10000 # 10k ohm
GPIO.setmode(GPIO.BCM)
instance = dht11.DHT11(pin=16)
GPIO.setwarnings(True)
GPIO.setup(26,GPIO.OUT,initial = GPIO.HIGH)
GPIO.setup(6,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
slack = slackweb.Slack
B=3950
REF=3.3 # 5.0 or 3.3
UpperLimitTemp1 = 330
UpperLimitTemp2 = 280
LowerLimitTemp1 = 330
LowerLimitTemp2 = 280
limit_mode =1

def main():
  count =0
  w.wiringPiSetup()
  w.wiringPiSPISetup(0,1000000)
  w.pinMode(0,1)
  w.pinMode(1,1)
  try:
    while 1:
      temp = temperature_out()
      #temp=15
      temp1=(MCP3008(4)/1024*5)/(4.07/1000)+temp
      temp2=(MCP3008(5)/1024*5)/(4.07/1000)+temp
 #     temp2=(MCP3008(4)/1024*5)/(4.07/1000)+temp
      if ( temp1 > UpperLimitTemp1 ) :
        w.digitalWrite(0,0)
        onflag0='OFF'
        slack_send("熱いからヒーターOFF!!")
      if ( temp1 < UpperLimitTemp2 ) :
        w.digitalWrite(0,1)
        onflag0='ON '
      if (( temp1 < UpperLimitTemp1) & (temp1 > UpperLimitTemp2 )) :
        if ( 1 == int( count / 5  ) % 2 ):
          w.digitalWrite(0,1)
          onflag0='ON '
        else:
          w.digitalWrite(0,0)
          onflag0='OFF'
          slack_send("熱いからヒーターOFF!!")
      if ( temp2 > LowerLimitTemp1 ) :
        w.digitalWrite(1,0)
        onflag1='OFF'
      if ( temp2 < LowerLimitTemp2 ) :
        w.digitalWrite(1,1)
        onflag1='ON '
      if (( temp2 < LowerLimitTemp1) & (temp2 > LowerLimitTemp2 )) :
        if ( 1 == int( count / 5  ) % 2 ):
          w.digitalWrite(1,1)
          onflag1='ON '
        else:
          w.digitalWrite(1,0)
          onflag1='OFF'


#     print ('{0} upper:{1:3.0f} C {2} lower:{3:3.0f} C {4} room temp:({5:2.0f} C)'.format(count,temp1,onflag0,temp2,onflag1,temp) )
      send = '{0} upper:{1:3.0f} C {2} lower:{3:3.0f} C {4} '.format(count,temp1,onflag0,temp2,onflag1)
      print (send)
      if count % 5 ==0:
       send = "{0} Now temperature is {1:3.0f}".format(count/5,(temp1-temp2)/2)
       slack_send(send)
      time.sleep(1)
      count=count+1
      if GPIO.input(6) == GPIO.HIGH and limit_mode == 1:
        if limit_mode ==1:
          limit_mode =0
        elif limit_mode==0:
          limit_mode =1
  except KeyboardInterrupt:
    w.digitalWrite(1,0)
    w.digitalWrite(0,0)

def gettemp():
  spiresult=MCP3008(0)
  if 0 == spiresult:
    spiresult=1 
#   thermistor_r = ( DIVR * (1024-spiresult ))/ (spiresult ) # thermistor is upper
  thermistor_r = ( DIVR * spiresult )/ (1024 -spiresult ) # // thermistor is lower
  t1 =   math.log( thermistor_r / THERMISTOR ) 
  baseTemp = ((298*B) / ( B + ( 298 * t1 ))) - 273 
#  print (thermistor_r)
  return (baseTemp)  

def MCP3008(channel):
  register = 0x80
  buff=(1 << 16) +(register<<8)+(channel<<12)
  buff=buff.to_bytes(3,byteorder='big') 
  w.wiringPiSPIDataRW(0,buff)
  return (((buff[1]&3)*256)+buff[2])

def temperature_out():
  result = instance.read()
  temp=result.temperature
  return temp

def slack_send(message):
    global limit_mode
    if limit_mode ==1:
      message = message+"今は上限300C"
    elif limit_mode == 0:
      message = message+"今は上限200C"
    slack = slackweb.Slack(url = "https://hooks.slack.com/services/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")
    slack.notify(text = message)
    
if __name__ == '__main__':
  main()
