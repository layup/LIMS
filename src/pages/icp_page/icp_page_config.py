from pages.icp_page.icp_reports import icp_report_setup
from pages.icp_page.icp_database import icp_history_setup
from pages.icp_page.icp_elements import icp_elements_setup

def icpSetup(self):     
    self.logger.info('Entering icpSetup')
    
    icp_history_setup(self)
    icp_elements_setup(self)
    icp_report_setup(self)
    
    # Connect signal 
    self.ui.icpTabWidget.currentChanged.connect(lambda index: on_icpTabWidget_currentChanged(self, index))

def on_icpTabWidget_currentChanged(self, index):
    self.logger.info(f'Entering on_icpTabWidget_currentChanged with index: {index}')
    
    if(index == 0): #History  
        self.ui.headerTitle.setText('ICP Database'); 
        self.ui.headerDesc.setText(''); 
    
    if(index == 1): # Elements Info 
        self.ui.headerTitle.setText('ICP Elements Information'); 

        totalElements = self.elementManager.getTotalElements()
        self.ui.headerDesc.setText("Total Elements: {}".format(totalElements))
        #loadDefinedElements(self)

    if(index == 2): #  Reports Info 
        self.ui.headerTitle.setText('ICP Reports Information'); 
        self.ui.headerDesc.setText(''); 

    