from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QDialog, QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, QTextEdit, QSpacerItem, QSizePolicy 
)

class SampleNameWidget(QWidget): 
    def __init__(self, labelName, valueName, parent=None): 
        super(SampleNameWidget ,self).__init__(parent)
    
        newName = str(valueName).strip()
    
        self.label = QLabel(labelName)
        self.label.setMaximumWidth(100)
        
        self.edit = QLineEdit(valueName)
        self.button = QPushButton()
        
        pixmapi = getattr(QStyle, 'SP_TitleBarCloseButton')
        icon = self.style().standardIcon(pixmapi)
        self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
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


#check for duplicates 
class CustomDialog(QDialog):
    def __init__(self, data, reportType):
        super().__init__()
        self.setWindowTitle('Custom Dialog')
        
        print(reportType)

        layout = QVBoxLayout()
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(data[0]))
        
        for row, rowData in enumerate(data):
            for column, columnData in enumerate(rowData):
                item = QTableWidgetItem(str(columnData))
                table_widget.setItem(row, column, item)
        layout.addWidget(table_widget)
        
        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.close)
        
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.accept)
        
        layout.addWidget(close_button)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        
    def save_sql(self): 
        pass; 

    def close(self): 
        print("Closing time")    
    
    def save(self): 
        print("Saving time")
        self.accept
    
    #metals 
    def icpMS(self): 
        pass; 

    #Text Files 
    def icpOES(self): 
        pass; 
    

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

