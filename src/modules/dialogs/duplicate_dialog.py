import os

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

class DuplicateDialog(QDialog):
    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name
        self.result = None

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'duplicate_dialog.ui')
        self.ui = loadUi(file_path, self)

        self.setWindowTitle("Duplicate Sample Options")

        self.setup()

    def setup(self):
        self.ui.message_label.setText(f'Would you live to overwrite or create a duplicate of the existing sample {self.job_name}')

        self.ui.duplicate_btn.clicked.connect(self.handle_duplicate)
        self.ui.overwrite_btn.clicked.connect(self.handle_overwrite)
        self.ui.cancel_btn.clicked.connect(self.handle_cancel)

        self.ui.overwrite_btn.setDefault(True)

    def handle_overwrite(self):
        self.result = 'overwrite'
        self.accept()

    def handle_duplicate(self):
        self.result = 'duplicate'
        self.accept()

    def handle_cancel(self):
        self.result = 'cancel'
        self.reject()

    @staticmethod
    def show_dialog(job_name):
        dialog = DuplicateDialog(job_name)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            return dialog.result
        else:
            return dialog.result
