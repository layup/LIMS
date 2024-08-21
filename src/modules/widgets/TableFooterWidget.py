import os
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget 

class TableFooterWidget(QWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')
            
        self.ui = loadUi(file_path, self)  # Pass 'self' as parent
        
    def load_data(self, current_page, total_rows, total_pages): 
        self.current_page = current_page
        self.total_rows = total_rows
        self.total_pages = total_pages
        
        # Update the pages 
        self.QSpinBox.setValue(current_page)
        self.QSpinBox.setMaximum(total_pages)
        self.pageLabel.setText(f'of {total_pages}')
    
        valid_rows = {100: 0, 200:1, 300:2}
        
        if(total_rows in valid_rows): 
            self.QComboBox.setCurrentIndex(valid_rows[total_rows])


''' TEST VERSION  
class TableFooterWidget(QWidget): 
    
    next_button_clicked = pyqtSignal(str)
    prev_button_clicked = pyqtSignal(str)
    combobox_edited = pyqtSignal(int)
    page_changed = pyqtSignal(int)
    
    #TODO: pass in the total pages and preferences
    #showRows 1 = 100, 2 = 200, 3 = 300 
    def __init__(self, totalPages, showRows=1, parent=None):
        super().__init__(parent)

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'tableFooterWidget.ui')

        #path = './ui/tableFooterWidget.ui'
        
        self.ui = loadUi(file_path, self)  # Pass 'self' as parent
        
        self.QSpinBox.setMaximum(totalPages)
        self.pageLabel.setText(f'of {totalPages}')
            
        # Connect the signals 
        self.nextBtn.clicked.connect(lambda:self.next_button_clicked.emit('Next'))
        self.prevBtn.clicked.connect(lambda:print('Prev Button'))
        self.QSpinBox.valueChanged.connect(lambda value: print(f'New Value: {value}'))
        self.QComboBox.currentIndexChanged.connect(lambda index: print(f'New Index: {index}'))
''' 