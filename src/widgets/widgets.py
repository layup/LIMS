


from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QDialog, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, QTextEdit, QSpacerItem, QSizePolicy 
)
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot

from modules.utilities import openFile, getFileLocation; 



#******************************************************************
#    Widgets 
#****************************************************************** 
class SampleNameWidget(QWidget): 
    def __init__(self, labelName, valueName, parent=None): 
        super(SampleNameWidget ,self).__init__(parent)
    
        newName = str(valueName).strip()
    
        self.label = QLabel(labelName)
        #self.label.setFixedWidth(60)
        self.edit = QLineEdit(valueName)
        
        self.button = QPushButton()
        pixmapi = getattr(QStyle, 'SP_TitleBarCloseButton')
        icon = self.style().standardIcon(pixmapi)
        self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(2)  # Adjust the spacing here
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        #layout.addWidget(self.button)
        
        self.setLayout(layout)

class SaveMessageBoxWidget(QWidget): 
    
    def __init__(self):
        super().__init__()
        
        self.error_popup()

    def removeDuplicate(self):
        print('def removeDuplicate(self): ...')
#        curItem = self.listWidget_2.currentItem()
#        self.listWidget_2.takeItem(curItem)

    def error_popup(self):
        msg = QMessageBox.critical(
            self, 
            'Title', 
            "You can't select more than one wicket-keeper", 
            QMessageBox.Yes | QMessageBox.Cancel
        )
        if msg == QMessageBox.Yes:
#            msg.buttonClicked.connect(self.removeDuplicate)
            print('Ok')
            self.removeDuplicate()


#******************************************************************
#    Dialog
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


#******************************************************************
#    Dialog
#****************************************************************** 
class FileLocationDialog(QDialog): 
    def __init__(self, preferences, parent=None):
        super().__init__()
        # Load the UI of the Dialog
        filePath = './ui/FileLocationDialog.ui' 
        loadUi(filePath, self)

        self.preferences = preferences
         
        self.tempPaths = self.preferences.values().copy()
        
        # set up the intial text Names 
        self.setupItems('TXTDirLocation', self.line1)
        self.setupItems('ispDataUploadPath', self.line2)
        self.setupItems('reportsPath', self.line3)
        self.setupItems('databasePath', self.line4)
        self.setupItems('officeDbPath', self.line5)

        # Connect the Buttons 
        self.closeBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.saveButtonClicked)
        
        # Connect the basic browse buttns  
        self.browse1.clicked.connect(lambda: self.browseForFolder('TXTDirLocation', self.line1))
        self.browse2.clicked.connect(lambda: self.browseForFolder('ispDataUploadPath', self.line2))
        self.browse3.clicked.connect(lambda: self.browseForFolder('reportsPath', self.line3))
        self.browse4.clicked.connect(lambda: self.browseForFile('databasePath', self.line4))
        self.browse5.clicked.connect(lambda: self.browseForFile('officeDbPath', self.line5))
     
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
