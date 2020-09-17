# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 13:40:24 2020
@author: ryan.robinson
ICE Commands: https://www.vescent.com/manuals/doku.php?id=ice
"""

import time
from serial import serialwin32 as serial


class ICE:
    def __init__(self,comNum):
        '''
        Initatizes the device
        Input: COM number [int]
        Output: None
        '''
        self.IceTimeout = .1 #Communication Timeout (seconds)
        self.IceByteRead = 256 #Number of bytes to read on ser.read()
        self.IceDelay = .01 #Delay in seconds after sending Ice Command to ensure execution
        self.comNum = int(comNum)
        try:
            self.IceSer = serial.Serial(port='COM'+str(int(self.comNum)),baudrate=115200,timeout=self.IceTimeout,parity='N',stopbits=1,bytesize=8)
        except:
            print("Could not open ICE on COM"+str(comNum))
        return None
        
    
    ###Functions###
    def setCard(self,SlotNum):
        '''
        Sets the active ice card
        Input: ICE Card Slot Number [int]
        Output: Active ICE Card Slot Number [int]
        '''
        print('Active slot: '+str(SlotNum))
        self.SlotNum = int(SlotNum)
        try:
            return self.send(('#slave '+str(self.SlotNum)))
        except:
            print("Failed to set slot number")
            self.close()
            return None
    
    def send(self,commandInput):
        '''
        Sends a command and returns the responsee
        Input: Command Input [str]
        Output: Command Output [str]
        '''
        # SEND ICE COMMAND
        command = (str(commandInput)+'\r\n').encode()
        print('Command Sent: '+commandInput)
        self.IceSer.write(command)
        time.sleep(self.IceDelay)
        
        # READ AND DECODE ICE OUTPUT
        response = self.IceSer.readline()
        time.sleep(self.IceDelay)
        try:
            print('ICE Response: '+response.decode())
            return response.decode()
        except:
            print('Failed to decode response, got: '+response)
            return response
            
    def close(self):
        self.IceSer.close()
        
# FOR TESTING PURPOSES
if __name__=="__main__":
    try:
        A = ICE(6)
        A.setCard(4)
        test = A.send("TempSet? 4")
        if "Invalid Command" in test:
            print("Wrong Slot")
    finally:
        A.close()
        
        
        
        
        
        