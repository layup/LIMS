import os

from base_logger import logger
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from modules.utils.file_utils import openFile, getFileLocation;

class FileLocationDialog(QDialog):
    def __init__(self, preferences, parent=None):
        super().__init__()

        self.preferences = preferences
        self.temp_paths = self.preferences.paths.copy()

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'FileLocationDialog.ui')
        loadUi(file_path, self)

        # set up the initial text Names
        self.setupItems('TXTDirLocation', self.line1)
        self.setupItems('ispDataUploadPath', self.line2)
        self.setupItems('reportsPath', self.line3)

        # Connect the Buttons
        self.closeBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.saveButtonClicked)

        # Connect the basic browse buttons
        self.browse1.clicked.connect(lambda: self.browseForFolder('TXTDirLocation', self.line1))
        self.browse2.clicked.connect(lambda: self.browseForFolder('ispDataUploadPath', self.line2))
        self.browse3.clicked.connect(lambda: self.browseForFolder('reportsPath', self.line3))

    def setupItems(self, pathName, lineItem):
        try:
            filePath = self.preferences.get_path(pathName)
            lineItem.setText(filePath)
        except Exception as error:
            print(error)

    @pyqtSlot()
    def browseForFile(self, pathName, lineItem):
        file_location = openFile()
        print(f'file_location: {file_location}')

        self.temp_paths[pathName] = file_location
        lineItem.setText(file_location)

    @pyqtSlot()
    def browseForFolder(self, pathName, lineItem):
        folder_location = getFileLocation()
        print(f'folder_location: {folder_location}')

        self.temp_paths[pathName] = folder_location
        lineItem.setText(folder_location)

    @pyqtSlot()
    def saveButtonClicked(self):
        self.preferences.update_paths(self.temp_paths)
        self.close()
