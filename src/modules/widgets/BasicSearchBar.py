
import os
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

class BasicSearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'searchBar.ui')

        self.ui = loadUi(file_path, self)  # Pass 'self' as parent


    def get_search_text(self):
        return self.searchLine.text()

