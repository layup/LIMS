#PYQT Imports 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QLineEdit
from PyQt5.Qt import Qt

#general Imports 
import sys 
import pandas as pd
import json
import sys 
import re 
import asyncio

from modules.utilities import * 
from ui.interface import Ui_MainWindow
from ui.GSMS_entry_page import Ui_GS_Entry

    
class MainWindow(QMainWindow):
    

    def __init__(self):
        super(MainWindow, self).__init__()
      
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) #self defined function that setups
        
        #define other widget setups 
        self.GSMSPageCreation()
        self.setWindowTitle("Tommy Lay") 


        #print(self.ui.page_3.ui.__dir__())
        #first page options 
        
        #self.ui.jobNumInput.textChanged.connect(lambda: print(self.ui.jobNumInput.text()))

        #connect menu buttons 
        self.ui.CreateReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.CreateReportPage))
        #self.ui.NextSection.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        self.ui.NextSection.clicked.connect(self.proceedPage)
        
        
        #self.ui.EditReportBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))
        self.ui.ViewReportBtn.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))
        self.ui.UploadBtn.clicked.connect(lambda: print(load_pickle('data.pickle')))
       
        #can have other keyboard modifiers as well 
        self.ui.stackedWidget.currentChanged.connect(lambda: print("Stacked Widget Changed "))
        
        #connect the menu bar options 
        #self.ui.subHeaderText.setText("Hello World")
        
        self.showMaximized()
        #self.show()
    
    #later problem 
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.test_method()
        if event.key() == Qt.Key_Space: 
            self.test_method()
        

    def test_method(self):
        print('Space key pressed')


    def saveJSONTest(self): 
        print("Saving json file")
        
        jsonLocation = getFileLocation()
        print(jsonLocation) 
        
        locaiton = '/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json'
        
        tempDictonary = {
            "TXTLOCATION":  jsonLocation
        }
        
        #serializing json data
        json_object = json.dumps(tempDictonary, indent=1)
        
        with open(locaiton, 'w') as outfile:
            outfile.write(json_object)
    
    def savePickle(self): 
        jsonLocation = getFileLocation()
        
        tempDictonary = {
            "JSONFileLocation":'/Users/layup/Documents/Programming/work /MB Labs/LIMS2.0/database/fileLocation.json', 
            "TXTDirLocation": jsonLocation 
        }
        
        save_pickle(tempDictonary)
        
    
    def proceedPage(self):
        print(self.ui.jobNumInput.text())
        
        #remove whitespaces 
        jobNum = self.ui.jobNumInput.text().strip()
        
        #make sure they entered all the valid information
        #have some style changes later on  
        if(re.match('^([0-9]{6})$', jobNum)): 
            print("valid job number")
            self.jobNum = jobNum; 
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
            
            #self.ui.labelJobNumHeader.setText("Hello World")
            self.ui.page_3.ui.labelJobNumHeader.setText("Job Number: " + "W" + jobNum)
            
            
            #scan for user information and setup page 
            tempLocation = scanForTXTFolders(self.jobNum)
            clientInfo, sampleNames = processClientInfo(self.jobNum, tempLocation)
            
            self.clientInfo = clientInfo 
            self.sampleNames = sampleNames
            
            #self.GSMS_loader(clientInfo, sampleNames)
            self.GSMS_loader()
            self.data_entry_loader(clientInfo['totalSamples']) 
            
            
        else: 
            msg = QMessageBox() 
            msg.setWindowTitle("Error to procceed")
            msg.setText("Please enter a valid job number!")
            x = msg.exec_()  # this will show our messagebox
            
    
    def GSMSPageCreation(self): 
        self.ui.page_3 = QtWidgets.QWidget()
        self.ui.page_3.ui = Ui_GS_Entry() 
        self.ui.page_3.ui.setupUi(self.ui.page_3)
        self.ui.page_3.setObjectName("page_3")
        self.ui.stackedWidget.addWidget(self.ui.page_3)
        
    #def GSMS_loader(self, clientInfo, samplesNames):
    #FIXME: issue arise when are adding the same widgets 
    #FIXME: free pointer references (not sure how but will find out )
    #TODO: when do we clear, when 1 generating the report, 
    def GSMS_loader(self): 
        print('loading the data')
        print(self.clientInfo)
        
        #add the clickEvents 
        #self.ui.page_3.ui.clientName.textChanged.connect()
        
        #self.ui.page_3.ui.
        #TODO: create a function 

        self.ui.page_3.ui.clientName.textChanged.connect(lambda: self.clientInfoChanged('clientName', self.ui.page_3.ui.clientName.text())) 
        
        #load the base models 
        self.ui.page_3.ui.clientName.setText(self.clientInfo['clientName'])
        self.ui.page_3.ui.date.setText(self.clientInfo['date'])
        self.ui.page_3.ui.time.setText(self.clientInfo['time'])
        self.ui.page_3.ui.attention.setText(self.clientInfo['attn'])
        self.ui.page_3.ui.addy1.setText(self.clientInfo['addy1'])
        self.ui.page_3.ui.addy2.setText(self.clientInfo['addy2'])
        self.ui.page_3.ui.addy3.setText(self.clientInfo['addy3'])
        self.ui.page_3.ui.sampleType.setText(self.clientInfo['sampleType1'])
        self.ui.page_3.ui.sampleType2.setText(self.clientInfo['sampleType2'])
        self.ui.page_3.ui.totalSamples.setText(self.clientInfo['totalSamples'])
        self.ui.page_3.ui.recvtemp.setText(self.clientInfo['recvTemp'])
        self.ui.page_3.ui.telephone.setText(self.clientInfo['tel'])
        self.ui.page_3.ui.email.setText(self.clientInfo['email'])
        self.ui.page_3.ui.fax.setText(self.clientInfo['fax'])
        self.ui.page_3.ui.payment.setText(self.clientInfo['payment'])
        
        #populate total sampleNames 
        totalSamples = len(self.sampleNames)
        print('Total Samples: ', totalSamples)
        #self.ui.page_3.ui.widget_4()
        #print(self.ui.page_3.ui.formLayout_2.count())  
        #print(self.ui.page_3.ui.formLayout_2.__dir__())

        counter = 0; 

        #TODO: might be easier if we just add one widget at a time sort of deal 
        temp = {}
        for key, value in self.sampleNames.items():
            #print(key,value)
            ''' 
            labelName = "sample" + str(counter) + "Label"
            lineEditName = "sample" + str(counter) + "Edit"

            setattr(self.ui.page_3.ui, lineEditName , QtWidgets.QLineEdit(self.ui.page_3.ui.widget_4))
            eval('self.ui.page_3.ui.%s.setObjectName("%s")' % (lineEditName, lineEditName))
            eval('self.ui.page_3.ui.formLayout_2.setWidget(%i, QtWidgets.QFormLayout.FieldRole, self.ui.page_3.ui.%s)' % (counter, lineEditName)) 
            
            setattr(self.ui.page_3.ui, labelName , QtWidgets.QLabel(self.ui.page_3.ui.widget_4))
            eval('self.ui.page_3.ui.%s.setObjectName("%s")' % (labelName, labelName))
            eval('self.ui.page_3.ui.formLayout_2.setWidget(%i, QtWidgets.QFormLayout.LabelRole, self.ui.page_3.ui.%s)' % (counter, labelName)) 
            
            eval('self.ui.page_3.ui.%s.setText("%s")' % (labelName, key) )
            eval('self.ui.page_3.ui.%s.setText("%s")' % (lineEditName, value) ) 
            
            #TODO: why is this so fucked up 
            changedText = eval('self.ui.page_3.ui.%s.text()' % lineEditName)
            
            #eval('self.ui.page_3.ui.%s.textChanged.connect(lambda: self.sampleInfoChanged(%s, %s, "%s") )' % (
            #    lineEditName, 
            #    key, 
            #    lineEditName, 
            #    "Hello World"
            #    
            #))
            
            counter+=1; 
            '''
            #so we start at zero 
            labelName = 'label' + str(counter)
            editName = 'edit' + str(counter)
            
            label = QtWidgets.QLabel(labelName, self.ui.page_3.ui.widget_4) 
            edit = QtWidgets.QLineEdit( editName, self.ui.page_3.ui.widget_4)
            
            temp[key] = [label,key]
        
            label.setText(key)
            edit.setText(value)
           
            
            self.ui.page_3.ui.formLayout_2.setWidget(counter, QtWidgets.QFormLayout.LabelRole, label )  
            self.ui.page_3.ui.formLayout_2.setWidget(counter, QtWidgets.QFormLayout.FieldRole, edit ) 
            #self.ui.page_3.ui.formLayout_2.addRow(label)
            #self.ui.page_3.ui.formLayout_2.addRow(edit) 
            #self.ui.page_3.ui.formLayout_2.insertRow(counter, label)
            #self.ui.page_3.ui.formLayout_2.insertRow(counter, edit)

            #edit.textChanged.connect(lambda: print(edit.text()))
           
            counter += 1; 
           
        #test = self.ui.page_3.ui.formLayout_2.findChild()
        
        count = self.ui.page_3.ui.formLayout_2.count()
        print(count)
        ''' 
        for x in range(count):
           
            try:
                item = self.ui.page_3.ui.formLayout_2.itemAt(x) 
                widget = item.widget()
                self.ui.page_3.ui.formLayout_2.removeWidget(widget)
            except: 
                print(x)
                pass
        '''
        
    
       
        
        for key, value in temp.items():
            #print(key, value)
            #print(value[1].text())
            
            #self.tester2(key,value)
            
            
            #self.ui.page_3.ui.formLayout_2.removeWidget(value[0])
            #self.ui.page_3.ui.formLayout_2.removeWidget(value[1])
             
            #self.ui.page_3.ui.formLayout.removeWidget(value[0])
            #self.ui.page_3.ui.formLayout.removeWidget(value[1]) 
            #value.textChanged.connect(lambda: print(key, value.text()));
            
            pass

        
        return; 
        
        
    
    def clientInfoChanged(self, propertyName, textChangeValue):
        temp = self.clientInfo
        temp[propertyName] = textChangeValue; 
        self.clientInfo = temp; 
        self.ui.page_3.ui.clientName.setText(self.clientInfo['clientName'])
        #print(self.clientInfo) 
        return;  
    
    
    #define the table from scratch and add connectors 
    #TODO: save items when the thing changes friends 
    def data_entry_loader(self, totalSamples): 
        print('loading the data boys')
        print(totalSamples)
        
        #self.ui.page_3.ui.tableWidget.setColumnCount(5)
        
        total_items = len(GSMS_values)
       
       #self.ui.page_3.ui.tableWidget(total_items) 
        
        
        
        
        
        
        
        
        
        
    
    def sampleInfoChanged(self, sampleName, objectName, textChangeValue): 
        print(sampleName)
        print(objectName)
        print(textChangeValue)
        temp = self.sampleNames 
        temp[sampleName] = textChangeValue;
        self.sampleNames = temp;  
        print(self.sampleNames)
        #update the text
        eval('self.ui.page_3.ui.%s.setText("%s")' % (objectName, textChangeValue)) 
        
        return 

def window(): 
    #global app, MainWindow 
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    MainWindow = MainWindow()
    #win = Mywindow()
    #win.show()
   
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    #window()
    import sys 
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    #win = Mywindow()
    #win.show()

    #for key, value in GSMS_values.items(): 
    #    print(key, value )

    #print(len(GSMS_values))
    
    sys.exit(app.exec_())