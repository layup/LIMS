from PyQt5.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QVBoxLayout, QDialog, 
    QMessageBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QStyle,
    QStyledItemDelegate, QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QSpacerItem, QSizePolicy
)


class SampleNameWidget(QWidget): 
    def __init__(self, labelName, valueName, parent=None): 
        super(SampleNameWidget ,self).__init__(parent)
    
        newName = str(valueName).strip()
    
        self.label = QLabel(labelName)
        self.edit = QLineEdit(valueName)
        self.button = QPushButton()
        
        pixmapi = getattr(QStyle, 'SP_TitleBarCloseButton')
        icon = self.style().standardIcon(pixmapi)
        self.button.setIcon(icon)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

  
        
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
    
