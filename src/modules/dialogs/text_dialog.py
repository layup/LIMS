from PyQt5.QtWidgets import (QPushButton, QDialog, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtPrintSupport import QPrintDialog


class TextFileDisplayDialog(QDialog):

    def __init__(self, text_file_path):
        super().__init__()
        self.setWindowTitle("Active Outgoing Jobs Lists")
        self.setFixedSize(800, 600)  # Set custom window size

        # Layout
        layout = QVBoxLayout(self)

        # TextEdit widget to display text
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # Button to print the text
        print_button = QPushButton("Print")
        print_button.clicked.connect(self.print_text)
        layout.addWidget(print_button)

        # Button to close the dialog
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


        # Read and display text from file
        self.load_text_file(text_file_path)

    def load_text_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                text = file.read()
                self.text_edit.setPlainText(text)
        except FileNotFoundError:
            self.text_edit.setPlainText("File not found.")

    def print_text(self):
        print('Printing text via printer')
        # Print the text

        print_dialog = QPrintDialog()
        if print_dialog.exec_() == QDialog.Accepted:
            # If the user accepts the dialog, print the text
            self.text_edit.print(print_dialog.printer())