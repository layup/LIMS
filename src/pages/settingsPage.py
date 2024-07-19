import os 
import sqlite3
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QTreeWidgetItem, QPushButton, QHBoxLayout, QWidget, QDialog
from PyQt5.QtCore import QObject, pyqtSignal


#from modules.dbManager import * 
from modules.dbFunctions import getAuthorInfo, getAllParameters, getAllAuthors 
#from modules.constants import *
from modules.utilities import load_pickle, save_pickle, getFileLocation, openFile
#from widgets.widgets import *


#TODO: update the localPrefernece stuff
def settingsSetup(self): 
    
    #load the intial settings 
    loadSettings(self) 
    
    settingsReportSetup(self)
    
    self.ui.SettingsTab.setCurrentIndex(0) 

    # Connect Buttons and Signals  
    self.ui.SettingsTab.currentChanged.connect(lambda index: settingsTab_changes(self, index))
    
    # File paths button signals 
    self.ui.reportsPathBtn.clicked.connect(lambda: updateFilePath(self.ui.reportPath, 'reportsPath'))
    self.ui.txtPathBtn.clicked.connect(lambda: updateFilePath(self.ui.txtPath, 'TXTDirLocation'))
    self.ui.convertedPathBtn.clicked.connect(lambda: updateFilePath(self.ui.convertPath, 'ispDataUploadPath'))
    
    # Database Connections 
    self.ui.dbPathBtn.clicked.connect(lambda: updateFileItem(self.ui.dbPath, 'databasePath'))
    self.ui.preferenceDbBtn.clicked.connect(lambda:updateFileItem(self.ui.prefrenceDbPath, 'preferencesPath'))


#TODO: I can have some more global functions that I can change
def settingsTab_changes(self, index):  
    
    if(index == 0): # General Tab 
        loadSettings(self) 

    if(index == 1): # Reports Tab 
        # clear the items 
        #self.ui.authorList.clear()
        #self.ui.authorNameLine.clear()
        #self.ui.authorPostionLine.clear()
        
        loadReportAuthors(self)

        # Load the report type section 
        loadReportParameters(self)

        # Load the parameters section 
        
        # Load the Authors section 
        
#******************************************************************
#    Preference Location Update 
#****************************************************************** 

#TODO: have a path object that will deal with all of the other bs that I have writen here 
def loadSettings(self): 
    self.ui.reportPath.setText(self.preferences.get('reportsPath'))
    self.ui.txtPath.setText(self.preferences.get('TXTDirLocation'))
    self.ui.convertPath.setText(self.preferences.get('ispDataUploadPath'))
    self.ui.dbPath.setText(self.preferences.get('databasePath'))
    self.ui.frontPath.setText(self.preferences.get('officeDbPath'))
    self.ui.prefrenceDbPath.setText(self.preferences.get('preferencesPath'))

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
        

        
#******************************************************************
#    Reports Functions 
#****************************************************************** 


def settingsReportSetup(self): 
    
    # Parameters setup 
    
    # button configuation setup 
    
    #Parameters Setup  
    parameterColumns = ['Parameter #', 'Parameter Name', 'Actions']
    self.ui.parameterTreeWidget.setHeaderLabels(parameterColumns)
    
    self.ui.parameterTreeWidget.setColumnWidth(0, 60) 
    self.ui.parameterTreeWidget.setColumnWidth(1, 220) 
    
    # Set the author tree labels 
    authorColumns = ['Author #', 'Author Name', 'Author Postion', 'Actions']
    #TODO: rename this to 
    self.ui.authorTreeWidget.setHeaderLabels(authorColumns)
    # Define Author Tree Column Widths     
    self.ui.authorTreeWidget.setColumnWidth(0, 60) 
    self.ui.authorTreeWidget.setColumnWidth(1, 220) 
    self.ui.authorTreeWidget.setColumnWidth(2, 220) 
    
    # Connect Signals 
    self.ui.addParamBtn.clicked.connect(lambda: add_parameter_btn_clicked(self.ui.parameterTreeWidget, self.tempDB))
    self.ui.addAuthorBtn.clicked.connect(lambda: add_author_btn_clicked(self.tempDB, self.ui.authorTreeWidget))

def add_author_btn_clicked(database, tree): 
    print(f'[FUNCTION]: add_author_btn_clicked')  

    dialog = authorDialog(database)
        
    dialog.updated_data.connect(lambda data: print(f'Updated Data: {data}')) 
        
    dialog.exec_() 

def add_parameter_btn_clicked(tree, database): 
    print(f'[FUNCTION]: add_parameter_btn_clicked')    
    
    dialog = parameterDialog(database)
        
    dialog.updated_data.connect(lambda data: print(f'Updated Data: {data}'))
        
    dialog.exec_() 
    
    #TODO: need to add this to the tree section 
    
def parameterHandler(): 
    pass; 
    
    
    

def loadReportParameters(self): 

    paramList = getAllParameters(self.tempDB)
    paramTreeWidget = self.ui.parameterTreeWidget
    
    # Clear the tree widget and reload the data 
    paramTreeWidget.clear()
    
    for paramItem in paramList: 
        paramNum, paramName = paramItem
   
        childTreeItem = QTreeWidgetItem(paramTreeWidget)
        childTreeItem.setText(0, str(paramNum))
        childTreeItem.setText(1, paramName)
    
        buttonWidget = parameterButtonItemWidget(paramNum, paramName, self.tempDB, paramTreeWidget, childTreeItem )

        paramTreeWidget.setItemWidget(childTreeItem, 2, buttonWidget)
        
def loadReportAuthors(self): 
    # Retrieve all of the authors information
    authorList = getAllAuthors(self.tempDB)
    authorTreeWidget = self.ui.authorTreeWidget 
    
    authorTreeWidget.clear()
    
    for i, authorItem in enumerate(authorList):         
        authorNum, authorName, authorRole = authorItem

        childTreeItem = QTreeWidgetItem(authorTreeWidget)
        childTreeItem.setText(0, str(authorNum)) #TODO: can set the item 
        childTreeItem.setText(1, authorName)
        childTreeItem.setText(2, authorRole)

        buttonWidget = ButtonItemWidget(authorNum, authorName, authorRole, self.tempDB, authorTreeWidget, childTreeItem)
        
        authorTreeWidget.setItemWidget(childTreeItem, 3, buttonWidget)
        
#******************************************************************
#    Reports Classes  
#******************************************************************  
    
class parameterButtonItemWidget(QWidget): 
    def __init__(self, paraNum, paraName, database, tree, treeItem, parent=None): 
        super().__init__(parent) 
        
        # Parameters 
        self.paraNum = paraNum
        self.paraName = paraName
        self.db = database
        self.tree = tree
        self.treeItem = treeItem
        
        # Button 
        self.editBtn = QPushButton('Edit')
        self.deleteBtn = QPushButton('Delete')

        self.editBtn.clicked.connect(self.handle_edit_button_clicked)
        self.deleteBtn.clicked.connect(self.handle_delete_button_clicked)

        # Layout  
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.addWidget(self.editBtn)
        layout.addWidget(self.deleteBtn)
        
        self.setLayout(layout)
        self.setFixedWidth(260)
        
    def handle_edit_button_clicked(self): 
        dialog = parameterDialog(self.db, self.paraName)
        
        dialog.updated_data.connect(self.handle_updated_data)
        
        dialog.exec_()      
    
    def handle_delete_button_clicked(self): 
        try:
            query = 'DELETE FROM parameters WHERE parameterNum= ?'
            self.db.execute(query, self.parameterNum)
            self.db.commit()

            self.tree.removeItemWidget(self.treeItem, self.treeItem.parent())

        except sqlite3.Error as e:
            print("Error:", e) 
    
    def handle_updated_data(self, data): 
        print(f'Handling Data: {data}')
        
        self.treeItem.setText(1, data)

    

class ButtonItemWidget(QWidget):
    def __init__(self, authorNum, authorName, authorPostion, database, tree, treeItem, parent=None):
        super().__init__(parent)
    
        # Parameters 
        self.num = authorNum
        self.name = authorName
        self.postion = authorPostion
        self.db = database
        self.tree = tree 
        self.treeItem = treeItem
        
        # Button 
        self.editBtn = QPushButton('Edit')
        self.deleteBtn = QPushButton('Delete')

        self.editBtn.clicked.connect(self.handle_edit_button_clicked)
        self.deleteBtn.clicked.connect(self.handle_delete_button_clicked)

        # Layout  
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  
        layout.addWidget(self.editBtn)
        layout.addWidget(self.deleteBtn)
        
        self.setLayout(layout)
        #self.setFixedSize(200,12) 
        self.setFixedWidth(260)
    
    def handle_edit_button_clicked(self): 
        #print(f'Current Row: {self.row}')
        
        dialog = authorDialog(self.db, self.num, self.name, self.postion)
        
        dialog.updated_data.connect(self.handle_updated_data)
        
        dialog.exec_()
    
    def handle_delete_button_clicked(self): 

        try:
            query = 'DELETE FROM authors WHERE authorNum = ?'
            self.db.execute(query, self.num)
            self.db.commit()

            self.tree.removeItemWidget(self.treeItem, self.treeItem.parent())

        except sqlite3.Error as e:
            print("Error:", e)

    
    def handle_updated_data(self, data): 
        print(f'Handling Data: {data}')
        
        self.treeItem.setText(0, data[0])
        self.treeItem.setText(1, data[1])
    
class authorDialog(QDialog): 
    
    updated_data = pyqtSignal(list)
    
    def __init__(self, database, authorNum=None, authorName=None, authorPostion=None):
        super().__init__()

        self.authorNum = authorNum 
        self.authorName = authorName
        self.authorPostion = authorPostion
        self.db = database 
        
        # load UI
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'addAuthorDialog.ui')
        loadUi(file_path, self)
        
        if(authorName and authorPostion): 
            self.authorNameLineEdit.setText(authorName)
            self.authorPostionLineEdit.setText(authorPostion)
            
        self.cancelBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.save_button_clicked)
        
        
    def save_button_clicked(self):
        currentName = self.authorNameLineEdit.text()
        currentPostion = self.authorPostionLineEdit.text()
        
        if(self.authorNum): 
            # Update to database 
            try: 
                query = 'UPDATE authors SET authorName = ?, authorRole = ? WHERE authorNum = ?' 
                self.db.execute(query, (currentName, currentPostion))
                self.db.commit()
            except Exception as error: 
                print(error)
            
        else: 
            # Save to Database 
            try: 
                query = 'INSERT INTO authors (authorName, authorRole) VALUES (?, ?)'
                self.db.execute(query, (currentName, currentPostion))
                self.db.commit()
            except Exception as error: 
                print(error)
         
        # Send updated data to update Tree
        self.updated_data.emit([currentName, currentPostion])
        self.close()

class parameterDialog(QDialog): 
    
    updated_data = pyqtSignal(str)

    def __init__(self, database, parameter=None):
        super().__init__()
        
        self.parameter = parameter
        self.db = database

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'addParameterDialog.ui')
        loadUi(file_path, self)  

        if(parameter): 
            self.parameterNameEdit.setText(parameter)

        self.cancelBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.save_button_clicked)

    def save_button_clicked(self): 
        parameterName = self.parameterNameEdit.text() 

        if(self.parameter): 
            # Update to database 
            try: 
                query = 'UPDATE parameters SET parameterName = ?' 
                self.db.execute(query, parameterName,)
                self.db.commit()
            except Exception as error: 
                print(error)
            
        else: 
            # Save to Database 
            try: 
                query = 'INSERT INTO parameters (parameterName) VALUES (?)'
                self.db.execute(query, parameterName)
                self.db.commit()
            except Exception as error: 
                print(error)
         
        # Send updated data to update Tree
        self.updated_data.emit(self.parameter)
        self.close()

            
    
    
    
    
    

    
