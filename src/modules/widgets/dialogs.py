import os 

from base_logger import logger
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QLabel, QHBoxLayout, 
    QPushButton, QDesktopWidget, QSpacerItem, QLineEdit, QTextEdit, 
    QSizePolicy, 
)
from PyQt5.uic import loadUi

from modules.utils.file_utils import openFile, getFileLocation; 

#******************************************************************
#    General Dialog 
#******************************************************************
def loadReportDialog(self): 
    self.logger.info('Entering loadReportDialog')
    msgBox = QMessageBox()  
    msgBox.setText("Report Already Exists");
    msgBox.setInformativeText("Would you like to load existing report or overwrite report?");
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Yes);
    
    x = msgBox.exec_()

    if(x == QMessageBox.Yes): 
        return 'Yes'
    if(x == QMessageBox.No):
        return 'No'
    if(x == QMessageBox.Cancel):
        return 'Cancel'
    
def showErrorDialog(self, errorTitle, errorMsg, detailedErrorMsg=None):
    logger.info('Entering showErrorDialog with parameters:')
    logger.error(f'errorTitle: {errorTitle}')
    logger.error(f'errorMsg: {errorMsg}')
        
    msg = QMessageBox()
    msg.setFixedWidth(400)
    msg.setIcon(QMessageBox.Information)

    msg.setText(errorTitle)
    msg.setInformativeText(errorMsg)
    
    if(detailedErrorMsg): 
        msg.setDetailedText(detailedErrorMsg)
        
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    retval = msg.exec_()
    print("value of pressed message box button:", retval)

def createdReportDialog(self, fileName): 
    self.logger.info(f'Entering createdReportDialog with parameters: fileName: {repr(fileName)}')
    msg = QMessageBox(self)
    #msg.setFixedWidth(7000)
    
    msg.setIcon(QMessageBox.Information)

    msg.setText('Success')
    msg.setInformativeText(f'Report successfully created. {fileName}')
        
    msg.setStandardButtons(QMessageBox.Ok )
    
    msg.exec_()
     

## Change QPushButton Checkable status when stackedWidget index changed
def messageBox(self):
    msgBox = QMessageBox()  
    msgBox.setText("The document has been modified.");
    msgBox.setInformativeText("Do you want to save your changes?");
    msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Save);
    
    x = msgBox.exec_()  # this will show our messagebox
    
    if(x == QMessageBox.Save): 
        self.ui.stackedWidget.setCurrentIndex(0)  
        self.activeCreation = False; 
    if(x == QMessageBox.Discard):
        self.ui.stackedWidget.setCurrentIndex(0) 
        self.activeCreation = False; 
    if(x == QMessageBox.Cancel):
        pass 
            

def deleteBox(self, title, message, action):
    msgBox = QMessageBox()  
    msgBox.setText(title);
    msgBox.setInformativeText(message);
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    x = msgBox.exec_() 
    
    if(x == QMessageBox.Yes): 
        return True
    if(x == QMessageBox.No):
        return False 

def replaceError(self,sampleName):
    msgBox = QMessageBox()  
    msgBox.setText("Duplicate Data?");
    message = 'There is sample named ' + str(sampleName) 
    
    msgBox.setInformativeText(message);
    msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save);
    msgBox.setDefaultButton(QMessageBox.Save);
    #msgBox.buttonClicked.connect(self.msgbtn)
    x = msgBox.exec_()  # this will show our messagebox
    
    if(x == QMessageBox.Save): 
        pass      

    if(x == QMessageBox.Cancel):
        pass 
    
    
#******************************************************************
#    CHM Dialog 
#******************************************************************
    
    

#******************************************************************
#    File  
#******************************************************************
class ChmTestsDialog(QDialog):
    def __init__(self, parent=None):
        super(ChmTestsDialog, self).__init__(parent)

        self.setWindowTitle("Add New Test Item")
        self.setFixedSize(600, 500)

        # Widgets
        self.display_name_label = QLabel("Display Name:")
        self.display_name_line = QLineEdit()

        self.txt_name_label = QLabel("TXT Name:")
        self.txt_name_line = QLineEdit()

        self.unit_type_label = QLabel("Unit Type:")
        self.unit_type_line = QLineEdit()

        self.default_standard_label = QLabel("Default Standard:")
        self.default_standard_line = QLineEdit()

        self.comments_label = QLabel("Comments:")
        self.comments_text = QTextEdit()

        self.ok_button = QPushButton("Save Test")
        self.cancel_button = QPushButton("Cancel")

        # Layout
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.display_name_label)
        input_layout.addWidget(self.display_name_line)

        input_layout.addWidget(self.txt_name_label)
        input_layout.addWidget(self.txt_name_line)

        input_layout.addWidget(self.unit_type_label)
        input_layout.addWidget(self.unit_type_line)

        input_layout.addWidget(self.default_standard_label)
        input_layout.addWidget(self.default_standard_line)

        input_layout.addWidget(self.comments_label)
        input_layout.addWidget(self.comments_text)

        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_user_input(self):
        result = self.exec_()
        
        if result == QDialog.Accepted:
            return {
                "display_name": self.display_name_line.text(),
                "txt_name": self.txt_name_line.text(),
                "unit_type": self.unit_type_line.text(),
                "default_standard": self.default_standard_line.text(),
                "comments": self.comments_text.toPlainText(),
            }
        else:
            return None


class FileLocationDialog(QDialog): 
    def __init__(self, preferences, parent=None):
        super().__init__()
        # Load the UI of the Dialog
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'FileLocationDialog.ui')
        loadUi(file_path, self)

        self.preferences = preferences
         
        self.tempPaths = self.preferences.values().copy()
        
        # set up the intial text Names 
        self.setupItems('TXTDirLocation', self.line1)
        self.setupItems('ispDataUploadPath', self.line2)
        self.setupItems('reportsPath', self.line3)
        self.setupItems('databasePath', self.line4)
        self.setupItems('officeDbPath', self.line5)
        self.setupItems('temp_backend_path', self.line6)

        # Connect the Buttons 
        self.closeBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.saveButtonClicked)
        
        # Connect the basic browse buttns  
        self.browse1.clicked.connect(lambda: self.browseForFolder('TXTDirLocation', self.line1))
        self.browse2.clicked.connect(lambda: self.browseForFolder('ispDataUploadPath', self.line2))
        self.browse3.clicked.connect(lambda: self.browseForFolder('reportsPath', self.line3))
        self.browse4.clicked.connect(lambda: self.browseForFile('databasePath', self.line4))
        self.browse5.clicked.connect(lambda: self.browseForFile('officeDbPath', self.line5))
        self.browse6.clicked.connect(lambda: self.browseForFile('temp_backend_path', self.line6))
     
    def setupItems(self, pathName, lineItem):
        try: 
            filePath = self.preferences.get(pathName)
            lineItem.setText(filePath) 
        except Exception as error: 
            print(error)

    @pyqtSlot()
    def browseForFile(self, pathName, lineItem): 
        fileLocation = openFile()
        print(f'file location: {fileLocation}')
        self.tempPaths[pathName] = fileLocation
        lineItem.setText(fileLocation)

    @pyqtSlot()  
    def browseForFolder(self, pathName, lineItem): 
        folderLocation = getFileLocation()
        print(f'Folder Location: {folderLocation}')
        self.tempPaths[pathName] = folderLocation
        lineItem.setText(folderLocation)
        

    @pyqtSlot()
    def saveButtonClicked(self): 
        
        for key, value in self.tempPaths.items():
            print(f'Updating: {key}: {value}')
            self.preferences.update(key, value)

        self.close()


    
#******************************************************************
#    Classes  
#******************************************************************
class openJobDialog(QDialog):
    def __init__(self, jobNum, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open")
        self.setFixedSize(300, 100)
        
        self.jobNum = jobNum
        
        self.center_on_screen()


        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(f"Do you want to open job number {self.jobNum}")
        layout.addWidget(label)

        button_layout = QHBoxLayout()  # Use QHBoxLayout for horizontal arrangement
        layout.addLayout(button_layout)

        yes_button = QPushButton("Yes")
        yes_button.clicked.connect(self.accept)
        button_layout.addWidget(yes_button)

        no_button = QPushButton("No")
        no_button.clicked.connect(self.reject)
        button_layout.addWidget(no_button)


    def center_on_screen(self):
        desktop_rect = QDesktopWidget().availableGeometry(self)
        self.move(desktop_rect.center() - self.rect().center())


 