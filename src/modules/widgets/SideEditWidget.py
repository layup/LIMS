import os

from PyQt5.QtCore import (Qt, pyqtSignal, QObject)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem
from PyQt5.uic import loadUi


class SideEditWidget(QWidget): 

    cancel_clicked = pyqtSignal(bool)
    save_clicked = pyqtSignal(list, QTreeWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.item = None;  
        self.disabled = False; 
        self.input_data = None;

        # Load UI elements
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'chmTestsEditSideWidget.ui')    
        self.ui = loadUi(file_path, self) 
        
        # Load general setup 
        self.init_setup()
        
        # Connect signals
        self.saveBtn.clicked.connect(self.on_save_clicked)
        
    def init_setup(self): 

        # allow only float values 
        float_validator = QDoubleValidator()
        float_validator.setDecimals(10)
        
        # allow only int values 
        int_validator = QIntValidator()
        
        # Set validators 
        self.jobNum.setValidator(int_validator)
        self.sampleNum.setValidator(int_validator)
        self.testsVal.setValidator(float_validator)
        self.standard.setValidator(int_validator)
        
        # set the limit to characters allowed in line edit 
        self.jobNum.setMaxLength(6)
        self.sampleNum.setMaxLength(6)
        self.testsVal.setMaxLength(30)

    def set_drop_down(self, parameterTypes, unitTypes):         
        for item in parameterTypes:
            self.testsNameCombo.addItem(item.testName, userData=item)

        self.unitValCombo.addItems(unitTypes)
        
        
    def set_data(self, data): 

        self.input_data = data;         
        
        self.jobNum.setText(data[0])
        self.sampleNum.setText(data[1])
        self.testsVal.setText(data[3])
        self.standard.setText(data[5])

        self.set_combo_widget(self.testsNameCombo, data[2])
        self.set_combo_widget(self.unitValCombo, data[4])
        
        # enable/disable combobox editing
        self.testsNameCombo.setDisabled(self.disabled)
        self.unitValCombo.setDisabled(self.disabled)
       
  
       
    def set_combo_widget(self, widget, itemName): 
        try: 
            index = widget.findText(itemName)
            
            if(index != -1): 
                widget.setCurrentIndex(index)
            
        except Exception as e: 
            print(e) 


    def get_data(self): 
        jobNum = self.jobNum.text()
        sampleNum = self.sampleNum.text()
        testsName = self.testsNameCombo.currentText()
        testsVal = self.testsVal.text()
        standardVal = self.standard.text()
        unitVal = self.unitValCombo.currentText()

        testNum = getParameterTypeNum(self.testsNameCombo)
        
        return [jobNum, sampleNum, testsName, testsVal, standardVal, unitVal, testNum]

    def clear_data(self): 
        self.jobNum.clear()
        self.sampleNum.clear()
        self.testsVal.clear()
        self.standard.clear()

    def set_combo_disabled(self, status:bool): 
        self.disabled = status; 


    def set_item(self, item): 
        self.item = item 
    
    def get_item(self): 
        return self.item
    
        
    def on_save_clicked(self): 
        result = self.get_data()
        #self.save_clicked.emit(result, self.current_row)

        self.save_clicked.emit(result, self.item);


class parameterItem: 
    def __init__(self,testNum, testName): 
        self.testNum = testNum
        self.testName = testName 

        
def getParameterTypeNum(comboBox): 
    
    index = comboBox.currentIndex()
    
    item = comboBox.itemData(index)
        
    return str(item.testNum)
    