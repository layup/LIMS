import os
import re 

from base_logger import logger
from PyQt5.QtWidgets import QFileDialog
from modules.utils.pickle_utils import save_pickle, load_pickle

def openFile(): 
    logger.info('Entering openFile')
    fileName, _ = QFileDialog.getOpenFileName(None, 'Open File', '',)
    return fileName

def getFileLocation():
    logger.info('Entering getFileLocation')
    dlg = QFileDialog().getExistingDirectory()
    print(dlg)
    return dlg


def saveNewLocation():
    location = getFileLocation() 
    text = input('Save File Name')
    
    save_pickle({text:location})

def determineFileType(file_path):
  """
  Checks the file extension to determine the file type.

  Args:
      file_path (str): Path to the file.

  Returns:
      str: The file extension (".txt" or ".xlsx").
  """
  return os.path.splitext(file_path)[1]

def scanDir(path): 
    logger.info(f'Entering ScanDir with parameter path: {path}')

    obj = os.scandir(path)
    #file = os.listdir(path)
    
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)
    
    obj.close()

def scanForTXTFolders(jobNum): 
    logger.info(f'Entering scanForTXTFolders with parameter jobNum: {jobNum}')
    
    fileLocationsDictionary = load_pickle('data.pickle')
    TXTLocation = fileLocationsDictionary['TXTDirLocation']
    locationsObject = os.scandir(TXTLocation)

    txtFolderLocations = [] 
    
    for entry in locationsObject: 
        if(entry.is_dir()):
            if(re.match('^TXT-[a-zA-Z]{3}$', entry.name)):
                txtFolderLocations.append(os.path.join(TXTLocation, entry.name))
            
    locationsObject.close()
    return processTXTFolders(jobNum, txtFolderLocations)
  
 
def processTXTFolders(jobNum, locations):
    logger.info(f'Entering processTXTFolders with parameter jobNum: {jobNum}, locations: {locations}')
    
    fileName = "W" + jobNum + ".TXT"
    
    for i in range(len(locations)): 
        tempLocationObject = os.scandir(locations[i]) 

        for entry in tempLocationObject: 
            if(entry.is_file()): 
                if(re.match(fileName, entry.name)): 
                    logger.info('TXT FILE FOUND')
                    #print(entry.name)
                    tempLocationObject.close()
                    return os.path.join(locations[i], entry.name)
        
        tempLocationObject.close()
    #TODO: return a blank user information 
    #can just clone the clientInfoDict somewhere and send it back 
    #print("No Job Number Matches")
    return None; 
