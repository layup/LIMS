
import sys
import os 
import re
import csv
import numpy
import inquirer
import json 
import sqlite3 
import pickle 




from PyQt5.QtWidgets import (
    QFileDialog
)

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
        'recieveTemp': '', 
        'tele': '', 
        'email': '', 
        'fax': '', 
        'payment': ''
    }
    
    #grab the file names 
    sampleNames = {}
    
    #have the information about the file, what kind of reports and etc 
    reportInformation = {}
    
    with open(fileLocation) as file: 
    
        lines = [line for line in file.readlines() if line.strip()]
        
        for lineLocation, line in enumerate(lines,1):
            print(lineLocation, line)
            
            
            if(lineLocation == 1): 
                print(lineLocation, line)
                clientInfoDict['clientName'] = line[0:54].strip()
                clientInfoDict['date'] = line[50:(54+7)].strip()
                clientInfoDict['time'] = line[66:71].strip()
                
            if(lineLocation == 2): 
                return; 
            
            
                
                     
        
        
    file.close()
    
    print(clientInfoDict)
    return clientInfoDict; 
    
    
