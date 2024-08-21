from PyQt5.QtWidgets import (QLabel, QLineEdit, QWidget, QHBoxLayout)

class SampleNameWidget(QWidget): 
    def __init__(self, labelName, valueName, parent=None): 
        super(SampleNameWidget ,self).__init__(parent)
    
        newName = str(valueName).strip()
    
        self.label = QLabel(labelName)
        self.edit = QLineEdit(valueName)
        
        #self.button = QPushButton()
        #pixalmap= getattr(QStyle, 'SP_TitleBarCloseButton')
        #icon = self.style().standardIcon(pixalmap)
        #self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(2)  # Adjust the spacing here
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        #layout.addWidget(self.button)
        
        self.setLayout(layout)