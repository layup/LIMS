
from PyQt5.QtWidgets import (QDialog, QMessageBox, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDesktopWidget)

class OpenJobDialog(QDialog):
    def __init__(self, jobNum, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open")
        self.setFixedSize(300, 100)

        self.jobNum = jobNum

        self.setup_ui()
        self.center_on_screen()

    def setup_ui(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(f"Do you want to open job number {self.jobNum}")
        layout.addWidget(label)

        button_layout = QHBoxLayout()  # Use QHBoxLayout for horizontal arrangement
        layout.addLayout(button_layout)

        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)

        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)


    def center_on_screen(self):
        desktop_rect = QDesktopWidget().availableGeometry(self)
        self.move(desktop_rect.center() - self.rect().center())