#!/usr/bin/env python3
import math
import time
import wiringpi as w 
from config_csv import ConfigJson as CJ
DIVR = 10000 # 4.7k ohm
THERMISTOR =10000 # 10k ohm
B=3950
REF=3.3 # 5.0 or 3.3
UpperLimitTemp1 = 330
UpperLimitTemp2 = 280
LowerLimitTemp1 = 330
LowerLimitTemp2 = 280

def main():
  count =0
  w.wiringPiSetup()
  w.wiringPiSPISetup(0,1000000)
  w.pinMode(0,1)
  w.pinMode(1,1)
  try:
    while 1:
#      temp=gettemp()
      temp=15
      temp1=(MCP3008(4)/1024*5)/(4.07/1000)+temp
      temp2=(MCP3008(5)/1024*5)/(4.07/1000)+temp
 #     temp2=(MCP3008(4)/1024*5)/(4.07/1000)+temp
      if ( temp1 > UpperLimitTemp1 ) :
        w.digitalWrite(0,0)
        onflag0='OFF'
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
      print ('{0} upper:{1:3.0f} C {2} lower:{3:3.0f} C {4} '.format(count,temp1,onflag0,temp2,onflag1) )
      time.sleep(1)
      count=count+1
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

if __name__ == '__main__':
  main()

