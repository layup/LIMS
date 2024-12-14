from modules.dbFunctions import get_total_chem_info_count

from pages.chm_page.history_tab.chm_history_config import chem_history_tab_setup
from pages.chm_page.reports_tab.chm_reports_config import chm_reports_tab_setup
from pages.chm_page.input_tab.chm_input_config import chm_input_tab_setup
from pages.chm_page.tests_tab.chm_tests_config import chm_tests_tab_setup

def chemistrySetup(self):
    self.logger.info('Entering chemistrySetup')

    chm_tests_tab_setup(self)
    chm_input_tab_setup(self)
    chem_history_tab_setup(self)
    chm_reports_tab_setup(self)

    # Connect the chem tab widget change function
    self.ui.chmTabWidget.currentChanged.connect(lambda index: on_chmTabWidget_currentChanged(self, index))

#TODO: reload in the data for all the sections (new data)?
def on_chmTabWidget_currentChanged(self, index):
    self.logger.info(f'Entering on_chmTabWidget_currentChanged with index: {index}')

    if(index == 0): # Database
        self.ui.headerTitle.setText('Chemistry Input Tests Database');
        self.ui.headerDesc.setText('');

    if(index == 1): # Input Data
        self.ui.headerTitle.setText('Chemistry Data Entry');
        self.ui.headerDesc.setText('');

    if(index == 2): # Test Info
        totalTests = get_total_chem_info_count(self.tempDB)
        self.ui.headerTitle.setText('Chemistry Tests Information');
        self.ui.headerDesc.setText(f'Total Tests: {totalTests}');

    if(index == 3): # Report Info
        self.ui.headerTitle.setText('Chemistry Reports Information')
        self.ui.headerDesc.setText('Total Reports: ')
