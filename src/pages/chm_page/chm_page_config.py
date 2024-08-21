from pages.chm_page.chm_history import chm_database_setup
from pages.chm_page.chm_reports import chm_report_setup
from pages.chm_page.chm_input import chm_input_setup
from pages.chm_page.chm_tests import chm_tests_setup

def chemistrySetup(self): 
    self.logger.info('Entering chemistrySetup')
    
    chm_tests_setup(self)
    chm_input_setup(self)
    chm_database_setup(self)
    chm_report_setup(self)

    # Connect the chem tab widget change function    
    self.ui.chmTabWidget.currentChanged.connect(lambda index: on_chmTabWidget_currentChanged(self, index))
    
#TODO: reload in the data for all the sections (new data)? 
def on_chmTabWidget_currentChanged(self, index): 
    self.logger.info(f'Entering on_chmTabWidget_currentChanged with index: {index}')
    
    if(index == 0): # Database 
        self.ui.headerTitle.setText('Chemistry Tests Database'); 
        self.ui.headerDesc.setText(''); 
        self.ui.editContainerWidget.setVisible(False)
        self.ui.chmEditWidget.setVisible(False)

    if(index == 1): # Input Data 
        self.ui.headerTitle.setText('Chemistry Data Entry'); 
        self.ui.headerDesc.setText(''); 
        
    if(index == 2): # Test Info  
        self.ui.headerTitle.setText('Chemistry Tests Information'); 
        self.ui.headerDesc.setText(''); 
        #totalTests = getChmTotalTests(self.db) 

    if(index == 3): # Report Info 
        self.ui.headerTitle.setText('Chemistry Reports Information')
        self.ui.headerDesc.setText('Total Reports: ') 
