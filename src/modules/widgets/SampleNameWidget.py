from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QLabel, QLineEdit, QWidget, QHBoxLayout, QPushButton)

class SampleNameWidget(QWidget):

    remove_btn_clicked = pyqtSignal(str)
    line_edit_changed = pyqtSignal(str, str)

    def __init__(self, labelName, sample_name, parent=None):
        super(SampleNameWidget ,self).__init__(parent)

        newName = str(sample_name).strip()

        self.label = QLabel(labelName)
        self.edit = QLineEdit(sample_name)
        self.edit.textChanged.connect(lambda updated_text: self.line_edit_changed.emit(labelName, updated_text))

        #self.button = QPushButton()
        #pixalmap= getattr(QStyle, 'SP_TitleBarCloseButton')
        #icon = self.style().standardIcon(pixalmap)

        self.button = QPushButton('Remove')
        self.button.clicked.connect(lambda: self.remove_btn_clicked.emit(labelName))
        #self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(2)  # Adjust the spacing here
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        #layout.addWidget(self.button)

        self.setLayout(layout)