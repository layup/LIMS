
import sys
import os 
import re
import csv
import numpy
import inquirer
import json 
import sqlite3 
import pickle 
from copy import copy




from PyQt5.QtWidgets import (
    QFileDialog
)

REPORTS_TYPE = {
    "ISP": "ISP", 
    "GSMS": "GSMS"
}

MATRIX_TYPE = {
    
}

PARAMETERS_TYPE = {
    
}


METHODS_TYPE = {
    
}

GSMS_values = {
    "001": ["ALkalinity", "mg/L"], 
    "002": ["NH3-N", "ug/L "], 
    "003": ["Cl-", 'mg/L'], 
    "004": ['E.C', 'us/cm'], 
    "005": ['F-', 'mg/L'], 
    "006": ['TKN', 'mg/L'], 
    "007": ['Mn', 'mg/L'], 
    "008": ['NO3-N', 'ug/L'], 
    "009": ['NO2-N', 'ug/L'], 
    "010": ['ortho-PO43', 'ug/L'],
    "011": ['pH', ' '], 
    "012": ['TPO43 --P', 'ug/L'], 
    "013": ['D.TO43 --P', 'ug/L'], 
    "014": ['SO42', 'mg/L'], 
    "015": ['T.O.C', 'mg/L'], 
    "016": ['T&L', 'mg/L'],
    "017": ['TDS', 'mg/L'], 
    "018": ['TSS', 'mg/L'],
    "019": ['Turbidity', 'NTU'], 
    "020": ['UVT', '%']
    
}

GSMS_So_values = {
    "001": 0.100, 
    '002': 0.254, 
    '003': ''
}

GSMS_ref_values = {
    "001": 100, 
    "002": 10, 
    "003": 10, 
        
}

GSMS_std_values ={
    
}



def save_pickle(dictonaryName):
    try:
        with open("data.pickle", "wb") as f:
            pickle.dump(dictonaryName, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def load_pickle(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)
 

def openFile(): 
    fileName, _ = QFileDialog.getOpenFileName(None, 'Open File', '',)
    #print(fileName)
    #print('Open FIle')
    return fileName

def getFileLocation():

    
    dlg = QFileDialog().getExistingDirectory()
    print(dlg)
    return dlg

def convertTXTFile(fileLocation): 

    return 

def convertCSVFile(fileLocation): 
    
    return 


def scanDir(path): 
    print("Scanning Dir: ", path)    
    
    #print(dir_path)
    obj = os.scandir(path)
    #file = os.listdir(path)
    
    
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)
    
        


    obj.close()

    

def scanForTXTFolders(jobNum): 
    print('jobnumber: ', jobNum)

    fileLocationsDictonary = load_pickle('data.pickle')
    TXTLocation = fileLocationsDictonary['TXTDirLocation']
    
    locationsObject = os.scandir(TXTLocation)
    
    txtFolderLocations = [] 
    
    for entry in locationsObject: 
        if(entry.is_dir()):
            if(re.match('^TXT-[a-zA-Z]{3}$', entry.name)):

                txtFolderLocations.append(os.path.join(TXTLocation, entry.name))
            
    
    #print(txtFolderLocations)
    locationsObject.close()
    return processTXTFolders(jobNum, txtFolderLocations)
  
 

def processTXTFolders(jobNum, locations):
    
    fileName = "W" + jobNum + ".TXT"
    
    #print("list")
    #print(locations)
   
    for i in range(len(locations)): 
        tempLocationObject = os.scandir(locations[i]) 

        for entry in tempLocationObject: 
            if(entry.is_file()): 
                if(re.match(fileName, entry.name)): 
                    print("TXT File found")
                    #print(entry.name)
                    tempLocationObject.close()
                    return os.path.join(locations[i], entry.name)
        
        tempLocationObject.close()
    #TODO: return a blank user information 
    #can just clone the clientInfoDict somewhere and send it back 
    print("No Job Number Matches")

        
def processClientInfo(jobNum, fileLocation):
    
    clientInfoDict = {
        'clientName': '', 
        'date': '', 
        'time': '', 
        'attn': '', 
        'addy1': '', 
        'addy2': '', 
        'addy3': '', 
        'sampleType1': '', 
        'sampleType2': '', 
        'totalSamples': '', 
        'recvTemp': '', 
        'tel': '', 
        'email': '', 
        'fax': '', 
        'payment': ''
    }
    
    #grab the file names 
    sampleNames = {}
    
    #have the information about the file, what kind of reports and etc 
    sampleTests = {}

    sampleCounter = 0; 
    prevLine = [0, ""]
    prevLineHelper = [0, ""]
    
    with open(fileLocation) as file: 
    
        for lineLocation, line in enumerate(file, 0):

            if(prevLine[0]+1 == prevLineHelper[0]):
                prevLine[0] = copy(prevLineHelper[0])
                prevLine[1] = copy(prevLineHelper[1])
                prevLineHelper[0] = copy(int(lineLocation))
                prevLineHelper[1] = copy(line)
            else: 
                prevLineHelper[0] = copy(int(lineLocation))
                prevLineHelper[1] = copy(line)
            

            #print('PrevLine: ', prevLine[0], prevLine[1])
            #print('PrevLineHelper: ', prevLineHelper[0], prevLineHelper[1])
            #print('currentLine: ', lineLocation, line)
        
                    
            if(lineLocation == 1): 
                clientInfoDict['clientName'] = line[0:54].strip()
                clientInfoDict['date'] = line[50:(54+7)].strip()
                clientInfoDict['time'] = line[66:71].strip()
                
            if(lineLocation == 2): 
                clientInfoDict['sampleType1'] = line[54:].strip()
                
                if "*" in line: 
                    clientInfoDict['attn'] = line[:54].strip()
                else: 
                    clientInfoDict['addy1'] = line[:54].strip()
                
            if(lineLocation == 3): 
                clientInfoDict['sampleType2'] = line[54:].strip()
                
                if(clientInfoDict['attn'] != ''):
                    clientInfoDict['addy1'] = line[:60].strip()
                else: 
                    clientInfoDict['addy2'] = line[:60].strip()
            
            if(lineLocation == 4): 
                clientInfoDict['totalSamples'] = line[60:].strip()
                
                if(clientInfoDict['attn'] != ''):
                    clientInfoDict['addy2'] = line[:60].strip()
                else: 
                    clientInfoDict['addy3'] = line[:60].strip() 
                    
            if(lineLocation == 5): 
                if(clientInfoDict['attn'] and clientInfoDict['addy2']): 
                    clientInfoDict['addy3'] = line[:60].strip()
                else: 
                    clientInfoDict['tel'] = line[26:50].strip()

                    try: 
                        clientInfoDict['recvTemp'] = line[71:].strip()
                    except:
                        print('No recv temp avaliable')
                        
            if(lineLocation == 6): 
                clientInfoDict['tel'] = line[26:50].strip() 
                clientInfoDict['recvTemp'] = line[71:].strip()
            
            if(lineLocation == 7): 
                clientInfoDict['fax'] = line[26:].strip()
                
            if(lineLocation == 8): 
                
                try: 
                    foundEmail = re.search('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', line).group()
                    if(foundEmail): 
                        clientInfoDict['email'] = foundEmail; 
                except:
                    print("email error")
                
                if("pd" in line.lower()): 
                    clientInfoDict['payment'] = line[51:].strip()
                     
            
            if(lineLocation > 35 and len(line) > 0): 
               
                if(sampleCounter != int(clientInfoDict['totalSamples']) ):

                    try: 
                        sampleMatch = re.search('(?<=\s[0-9]).*', line).group()
                        if(sampleMatch): 
                            sampleName = str(jobNum) + '-' + str(sampleCounter+1)
                            sampleNames[sampleName] = sampleMatch.strip()
                            sampleCounter+=1; 
                           
                        #TODO: add something to get the - afterwords 
                    except: 
                        pass
                #find the report information that does with corrisponding thing                
                if(re.search('(?<=\s-\s).*', line)):
                    prevSampleName = str(jobNum) + "-" + str(sampleCounter-1)
                    print(prevSampleName)
                    currentTestsCheck = re.search('(?<=\s-\s).*', line)
                    prevSampleMatchCheck = re.search('(?<=\s[0-9]).*', prevLine[1])
                    prevSampleTestsCheck = re.search('(?<=\s-\s).*', prevLine[1])
                    #sampleTests[prevSampleName] = currentTestsCheck.group()
                    #not could be apart of the string name longer 
                    
                    #add to most recent sample
                    if(currentTestsCheck):
                        #print('current is a test: ', currentTestsCheck.group())
                        sampleTests[prevSampleName] = currentTestsCheck.group()


                    if(prevSampleMatchCheck):
                        #print('prev was a sampleName')
                        #print(sampleName[prevSampleName]) #doesnt work 
                        pass; 
                       
                    #append onto them 
                    if(prevSampleTestsCheck):
                        sampleTests[prevSampleName] = sampleTests[prevSampleName]  + ", " + currentTestsCheck.group()
                        
                    #TODO: solve this later, add previous name onto current name sample 
                    if((not bool(prevSampleMatchCheck)) and not( bool(prevSampleTestsCheck))): 
                        print('prev was apart of the name yo')
                        
                        
            
            #print('---------------------------') 
                
                    
                     
            
            
                    
        
    file.close()
    
    #print(clientInfoDict)
    #print(sampleNames)
    #print(sampleTests)
    return clientInfoDict, sampleNames; 
    
    
