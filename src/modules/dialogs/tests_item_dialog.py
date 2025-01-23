import os



from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSignal

from PyQt5.QtWidgets import QTreeWidgetItem, QDialog

class TestsItemDialog(QDialog):

    new_data = pyqtSignal(list)

    def __init__(self, title, test_id=None, test_info = None):
        super().__init__()

        self.test_id = test_id
        self.test_info = test_info
        self.title = title

        # Load the UI File
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'addTestsDialog.ui')
        self.ui = loadUi(file_path, self)

        #set the titles
        self.setWindowTitle(title)
        self.title.setText(title)

        # Connect the buttons
        self.cancelBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.handle_save_btn)

        self.init_setup()


    def init_setup(self):

        self.comment.setMaxLength(26)

        if(self.test_info):
            self.test_name.setText(self.test_info[0])
            self.text_name.setText(self.test_info[1])
            self.display_name.setText(self.test_info[2])
            self.comment.setText(self.test_info[3])


    def handle_save_btn(self):
        test_name = self.test_name.text()
        text_name = self.text_name.text()
        display_name = self.display_name.text()
        side_comment = self.comment.text()

        if(self.test_id):
            self.new_data.emit([test_name, text_name, display_name, side_comment])