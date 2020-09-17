# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 16:56:42 2020

@author: ryan.robinson

Created for the AMPAC system.

Function:
    Turns off all lasers and temp loops for the AMPAC system
"""

import ICEDevice
from StartUp import SetValues

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
        
        ''' TURN ALL SOAS OFF '''
        Boxes[1].setCard(str(6))
        Boxes[1].send("Laser 1 Off")
        Boxes[1].send("Laser 2 Off")
        
        ''' TURN ALL LASERS OFF '''
        for currData in D.currSet:
            Boxes[int(currData[D.box])].setCard(str(currData[D.card]))
            Boxes[int(currData[D.box])].send("Laser Off")
        
        ''' VERIFY THAT ALL LASERS ARE OFF '''
        laserstatus = []
        for currData in D.currSet:
            Boxes[int(currData[D.box])].setCard(str(currData[D.card]))
            laserstatus.append(Boxes[int(currData[D.box])].send("Laser?").strip("\n"))
        print(laserstatus)
        if "On" in laserstatus:
            raise Exception("Failed to shutdown lasers, leaving temp loops on")
        
        ''' TURN OFF ALL SERVOS '''
        for tempData in D.tempSet:
            print(tempData)
            # SET CARD
            Boxes[int(tempData[D.box])].setCard(str(tempData[D.card]))
            # STOP SERVO
            Boxes[int(tempData[D.box])].send(" ".join(["Servo",str(tempData[D.chan]),"Off"]))
            

            
    finally:
        # CLOSE ALL ICE BOXES
        for Box in Boxes:
            Box.close()
              
    return None







if __name__ == "__main__":
    main()