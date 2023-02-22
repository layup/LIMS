
import sys
import os 
import re
import csv
import numpy
import inquirer
import json 
import sqlite3 





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
    print("Scanning Dir")    
    
     #print(dir_path)
    obj = os.scandir(path)
    file = os.listdir(path)
    
    
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)
    

    obj.close()
    



    
    



