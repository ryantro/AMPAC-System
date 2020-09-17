# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 17:02:13 2020

@author: ryan.robinson

Created for the AMPAC system.


Function:
    Turns on all temp loops for the AMPAC system and waits for them to stabilize.
"""

import ICEDevice
import csv
import time

def main():
    # FILEPATH OF SETVALUES CSV
    tempfilename = "tempsetvalues.csv"
    currentfilename = "currentsetvalues.csv"
    comfilename = "comportvalues.csv"
    
    # PARSE SET VALUES FILE AND CREATE A DATA OBJECT, D
    D = SetValues()
    D.genTempData(tempfilename)
    D.genCurrentData(currentfilename)
    D.genComPorts(comfilename)
    
    
    try:
        # OPEN ALL ICE BOXES
        Boxes = []
        for comPort in D.comPorts:
            Boxes.append(ICEDevice.ICE(int(comPort)))
        
        ''' VERIFY THAT THE CORRECT COM PORT IS SPECIFIED FOR BOX ICE BOXES '''
        # VERIFY box1COM CORRESPONDS TO BOXES[0]
        Boxes[0].setCard(str(4))
        test = Boxes[0].send("TempSet? 4")
        if "Invalid Command" in test:
            raise Exception("ICE BOX #1 is not on the correct COM port")
        # VERIFY box2COM CORRESPONDS TO BOXES[1]
        Boxes[1].setCard(str(3))
        test = Boxes[1].send("TempSet? 4")
        if "Invalid Command" in test:
            raise Exception("ICE BOX #2 is not on the correct COM port")
        
        ''' SET ALL SETTING WITH RESPECT TO TEMPERATURE AND START SERVO '''
        for tempData in D.tempSet:
            print(tempData)
            Boxes[int(tempData[D.box])].setCard(str(tempData[D.card]))                                          # SET CARD
            Boxes[int(tempData[D.box])].send(" ".join(["TempSet",str(tempData[D.chan]),str(tempData[D.tset])])) # SET TEMP
            Boxes[int(tempData[D.box])].send(" ".join(["TempMin",str(tempData[D.chan]),"10"]))                  # SET TEMP MIN
            Boxes[int(tempData[D.box])].send(" ".join(["TempMax",str(tempData[D.chan]),"35"]))                  # SET TEMP MAX
            Boxes[int(tempData[D.box])].send(" ".join(["Gain",str(tempData[D.chan]),str(tempData[D.gain])]))    # SET GAIN
            Boxes[int(tempData[D.box])].send(" ".join(["Servo",str(tempData[D.chan]),"On"]))                    # START SERVO
            
        ''' CHECK AND WAIT FOR TEMPERATURE STABILITY '''
        # CREATE THE OBJECT IN CHARGE OF TRACKING AND MEASURING TEMPERATURE STABILITY
        T = TempCheck()
        
        # FOR TESTING
        # T.setMinError(0)
        
        # DEFINE PAMETERS
        starttime = time.time()
        timeouttime = 60*6
        
        # LOOP UNTIL TEMPERATURES ARE STABLE AND ERROR TEMP IS UNDER 5MK
        tErrors = []
        tempStablized = False
        while tempStablized == False:
            # READ OUT TEMP ERROR SIGNALS FROM ALL TEMP LOOPS AND PUT THEM IN TERRORS
            for tempData in D.tempSet:
                # SET CARD NUMBER
                Boxes[int(tempData[D.box])].setCard(str(tempData[D.card]))
                # MEASURE ERROR SIGNAL
                tErrors.append(Boxes[int(tempData[D.box])].send(" ".join(["TError?",str(tempData[D.chan])]))) 
            # CHECK IF ERRORS TEMPS ARE WITHIN 5MK
            T.errorTempCheck(tErrors)
            tErrors.clear()
            # CHECK IF TEMPERATURE IS STABILIZED OVER CONSECUTIVE MEASUREMENTS
            tempStablized = T.checkStablized()           
            # WAIT 1 SECOND 
            time.sleep(1)            
            # CHECK FOR TIMOUT
            if timeouttime < (time.time()-starttime):
                raise TimeoutError("Could not stablize temp loops.")
                
        # ALL TEMPERATURES ARE STABILIZED AT THIS POINT
        print("All temp loops sucessfully stabilized at t = "+str(time.time()-starttime))
            
        ''' TURN LASERS ON '''
        for currData in D.currSet:
            Boxes[int(currData[D.box])].setCard(str(currData[D.card]))                      # SET CARD
            Boxes[int(currData[D.box])].send(" ".join(["CurrLim",str(currData[D.clim])]))   # SET CURRENT LIMIT
            Boxes[int(currData[D.box])].send(" ".join(["CurrSet",str(currData[D.cset])]))   # SET CURRENT
            Boxes[int(currData[D.box])].send("Laser On")                                    # TURN LASER ON
            
    finally:
        # CLOSE ALL ICE BOXES
        for Box in Boxes:
            Box.close()
    
    ''' RUN THE ICE GUI '''
    # try:
    #     os.system(icegui)
    # except:
    #     print('Unable to open ICE GUI. Please open manually')
    #     pass
    
    return None

class TempCheck:
    '''Object responsible for verifying that temp loops are stable'''
    def __init__(self):
        self.checks = [False, False, False, False, False]
        self.index = 0
        self.minerror = 0.005
        return None
    
    def errorTempCheck(self,errorTempList):
        '''Checks if all error temperatures are within limit'''
        # USER DEFINED TEMP ERROR VIA setMinError COMMAND
        self.checks[self.index] = all(float(x) < self.minerror for x in errorTempList)
        
        # INCREMENT OR WRAP THE INDEX
        self.index += 1
        if self.index >= len(self.checks):
            self.index = 0
        
        return None
    
    def setMinError(self,minerror):
        '''Sets the minimum error value for all temp loops'''
        self.minerror = minerror
        return None
    
    def checkStablized(self):
        '''Returns True if the checks array is all true'''
        print(self.checks)
        if False in self.checks:
            return False
        else:
            return True

class SetValues:
    def __init__(self):
        '''
        Parses the set values file.
        Input: Set values file [str]
        Output: None
        '''
        
        # INDECIES OF SETVALUES FILE
        self.box = 0
        self.card = 1        

        return None

    def genTempData(self,inputfile):
        '''
        Loads the temp data from tempsetvalue and stores it in self.tempSet
        Input: inputfile [str]
        '''
        # INDECIES OF SETVALUES FILE
        self.chan = 2
        self.tset = 3
        self.gain = 4
        
        # TEMP SET ARRAY
        self.tempSet = []
        with open(inputfile,encoding='utf-8-sig', mode='r') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            for row in rows:
                if("Temp" in row[0]):
                    self.tempSet.append([row[1],row[2],row[3],row[4],row[5]])
        return None
    
    def genCurrentData(self,inputfile):
        '''
        Loads the current data from currentsetvalue and stores it in self.currSet
        Input: inputfile [str]
        '''        
        # INDECIES OF SETVALUES FILE
        self.cset = 2
        self.clim = 3
        
        # TEMP SET ARRAY
        self.currSet = []
        with open(inputfile,encoding='utf-8-sig', mode='r') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            for row in rows:
                if("Current" in row[0]):
                    self.currSet.append([row[1],row[2],row[3],row[4]])
        return None
        
    def genComPorts(self,inputfile):
        '''
        Generates a list of COM ports in order from the first icebox to the last and stores it in self.comPorts
        Input: inputfile [str]
        '''
        # INDECIES OF SETVALUES FILE
        self.com = 1
        
        # COM PORT ARRAY
        self.comPorts = []
        tempArr = []
        with open(inputfile,encoding='utf-8-sig', mode='r') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            for row in rows:
                if("COM-" in row[0]):
                    self.comPorts.append([row[1],row[2]])
                    tempArr.append(row[2])
                    
        # SORT THE LIST AND STORE IN A TEMP ARRAY
        for comPort in self.comPorts:
            tempArr[int(comPort[0])] = comPort[1]
            
        # REASSIGN COM PORTS
        self.comPorts = tempArr
        return None

if __name__ == "__main__":
    main()