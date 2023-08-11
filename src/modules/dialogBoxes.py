from PyQt5.QtWidgets import QDialog, QMessageBox

def loadReportDialog(self): 
    msgBox = QMessageBox()  
    msgBox.setText("Report Already Exists");
    msgBox.setInformativeText("Would you like to load existing report or overwrite report?");
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Yes);
    
    x = msgBox.exec_()

    if(x == QMessageBox.Yes): 
        pass
        #FIXME: load in the values as well 
    if(x == QMessageBox.No):
        pass 
    if(x == QMessageBox.Cancel):
        pass 
    
def showErrorDialog(self, errorTitle, errorMsg, detailedErrorMsg=None):
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText(errorTitle)
    msg.setInformativeText(errorMsg)
    
    if(detailedErrorMsg): 
        msg.setDetailedText(detailedErrorMsg)
        
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    retval = msg.exec_()
    print("value of pressed message box button:", retval)


## Change QPushButton Checkable status when stackedWidget index changed
def messageBox(self):
    msgBox = QMessageBox()  
    msgBox.setText("The document has been modified.");
    msgBox.setInformativeText("Do you want to save your changes?");
    msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel);
    msgBox.setDefaultButton(QMessageBox.Save);
    #msgBox.buttonClicked.connect(self.msgbtn)
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
    msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    x = msgBox.exec_() 
    
    if(x == QMessageBox.Yes): 
        pass
    if(x == QMessageBox.No):
        pass 

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