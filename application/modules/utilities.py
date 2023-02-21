
import sys
import os 
import re
import csv
import numpy
import inquirer
import json 


from PyQt5.QtWidgets import (
    QFileDialog
)

def openFile(): 
    fileName, _ = QFileDialog.getOpenFileName(None, 'Open File', '',)
    
    print(fileName)
    #print('Open FIle')
    return fileName

def getFiles():
    dlg = QFileDialog().getExistingDirectory()
    print(dlg)
    return dlg


def scanDir(path): 
    print("Scanning Dir")    
    
     #print(dir_path)
    obj = os.scandir(path)
    file = os.listdir(path)
    
    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)
    

    obj.close()



    
    



