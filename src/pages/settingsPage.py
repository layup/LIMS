
import sqlite3
from PyQt5.QtCore import pyqtSlot

#from modules.dbManager import * 
from modules.dbFunctions import getAuthorInfo
#from modules.constants import *
from modules.utilities import load_pickle, save_pickle, getFileLocation, openFile
#from widgets.widgets import *

def settingsSetup(self): 
    loadSettings(self) 
    self.ui.SettingsTab.setCurrentIndex(0) 


    # Connect Buttons and Signals  
    self.ui.SettingsTab.currentChanged.connect(lambda index: settingsTab_changes(self, index))
    
    reportPathWidget = self.ui.reportPath
    textPathWidget = self.ui.txtPath
    fileConvertedPathWidget = self.ui.convertPath
    databasePathWidget = self.ui.dbPath

    self.ui.reportsPathBtn.clicked.connect(lambda: updateFilePath(reportPathWidget, 'reportsPath'))
    self.ui.txtPathBtn.clicked.connect(lambda: updateFilePath(textPathWidget, 'TXTDirLocation'))
    self.ui.convertedPathBtn.clicked.connect(lambda: updateFilePath(fileConvertedPathWidget, 'ispDataUploadPath'))
    self.ui.dbPathBtn.clicked.connect(lambda: updateFileItem(databasePathWidget, 'databasePath'))

    self.ui.saveAuthorBtn.clicked.connect(lambda: on_saveAuthorBtn_clicked(self)) 
    self.ui.deleteAuthorBtn.clicked.connect(lambda: on_deleteAuthorBtn_clicked(self))
    
    self.ui.authorList.currentItemChanged.connect(lambda authorName: on_authorList_currentItemChanged(self,authorName))
    self.ui.addAuthor.clicked.connect(lambda: on_addAuthor_clicked(self))


#TODO: I can have some more global functions that I can change
def settingsTab_changes(self, index):  
    
    authorList = self.ui.authorList 

    if(index == 0): 
        loadSettings(self) 

    if(index == 1): 
        #clear the items 
        self.ui.authorList.clear()
        self.ui.authorNameLine.clear()
        self.ui.authorPostionLine.clear()
        
        loadAuthors(self.db, authorList)
        
#******************************************************************
#    Preference Location Update 
#****************************************************************** 

#TODO: have a path object that will deal with all of the other bs that I have writen here 
def loadSettings(self): 
    self.ui.reportPath.setText(self.paths['reportsPath'])
    self.ui.txtPath.setText(self.paths['TXTDirLocation'])
    self.ui.convertPath.setText(self.paths['ispDataUploadPath'])
    self.ui.dbPath.setText(self.paths['databasePath'])

@pyqtSlot() 
def updateFilePath(widget, pathName): 
    paths = load_pickle('data.pickle')
    # Get the file Locatioin 
    newFilePath = getFileLocation()
    if(newFilePath != '' and newFilePath != None): 
        paths[pathName] = newFilePath 
        save_pickle(paths)
        #TODO: maybe return the paths so I can update self.path 
        widget.setText(paths[pathName])
        
@pyqtSlot()       
def updateFileItem(widget, pathName): 
    paths = load_pickle('data.pickle')
    # Open the file 
    newFilePath = openFile() 
    
    if(newFilePath != '' and newFilePath != None): 
        paths[pathName] = newFilePath 
        save_pickle(paths)
        widget.setText(paths[pathName]) 
        
    
def loadAuthors(database, authorList): 
    authorsQuery = 'SELECT * FROM authors ORDER BY authorName ASC'

    try: 
        results = database.query(authorsQuery)
        print('Loading Authors')
        print(results)
        for author in results: 
            authorList.addItem(author[0])
        
    except: 
        print('Error: could not load authors')
    
#******************************************************************
#    Author Functions 
#****************************************************************** 
@pyqtSlot()  
def on_saveAuthorBtn_clicked(self): 
    authorName = self.ui.authorNameLine.text()
    authorPosition = self.ui.authorPostionLine.text()
    
    if((authorName != None or '') and (authorPosition != None or "")): 
        sql = 'INSERT OR REPLACE INTO authors (authorName, authorPosition) VALUES (?,?)'
        try:
            self.db.execute(sql, (authorName, authorPosition,) )
            self.db.commit()

        except sqlite3.IntegrityError as e:
            print(e) 
    
@pyqtSlot()  
def on_deleteAuthorBtn_clicked(self): 
    deleteQuery = 'DELETE FROM authors WHERE authorName = ?' 
    authorName = self.ui.authorList.currentItem().text() 
    
    try: 
        self.db.execute(deleteQuery, (authorName,))
        self.db.commit()
        removeAuthorFromAuthorList(self, authorName)
    except:
        print("Error: Could not delete author: ", authorName)

def on_authorList_currentItemChanged(self, authorName):   
    if(authorName != None):  
        loadAuthorInfo(self, authorName.text())

def removeAuthorFromAuthorList(self, authorName): 
    for row in range(self.ui.authorList.count()): 
        item = self.ui.authorList.item(row)
        if item.text() == authorName: 
            self.ui.authorList.takeItem(row)
            break;         


def loadAuthorInfo(self, authorName):             
    result = getAuthorInfo(self.db, authorName) 
    
    if(result): 
        self.ui.authorNameLine.setText(result[0])
        self.ui.authorPostionLine.setText(result[1])
    else: 
        print("Error loading author info")
        self.ui.authorNameLine.clear()
        self.ui.authorPostionLine.clear()
        self.ui.enterAuthorName.clear()
        self.ui.authorNameLine.setText(authorName)
        

@pyqtSlot()  
def on_addAuthor_clicked(self): 

    authorName = self.ui.enterAuthorName.text()

    sql = "SELECT authorName FROM authors"
    result = self.db.query(sql)
    
    print(result)
    
    if(authorName != ''): 
        self.ui.authorList.addItem(authorName)
        self.ui.authorNameLine.setText(authorName)
        
        new_item_index = self.ui.authorList.count() - 1
        self.ui.authorList.setCurrentRow(new_item_index)