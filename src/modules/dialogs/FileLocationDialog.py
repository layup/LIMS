import os

from base_logger import logger
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from modules.utils.file_utils import openFile, getFileLocation;

class FileLocationDialog(QDialog):
    def __init__(self, preferences, parent=None):
        super().__init__()
        # Load the UI of the Dialog
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'FileLocationDialog.ui')
        loadUi(file_path, self)

        self.preferences = preferences

        self.tempPaths = self.preferences.values().copy()

        # set up the initial text Names
        self.setupItems('TXTDirLocation', self.line1)
        self.setupItems('ispDataUploadPath', self.line2)
        self.setupItems('reportsPath', self.line3)
        self.setupItems('databasePath', self.line4)
        self.setupItems('officeDbPath', self.line5)
        self.setupItems('temp_backend_path', self.line6)

        # Connect the Buttons
        self.closeBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.saveButtonClicked)

        # Connect the basic browse buttons
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
