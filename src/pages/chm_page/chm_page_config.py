from modules.dbFunctions import get_total_chem_info_count

from pages.chm_page.history_section.chm_history_config import chm_database_setup
from pages.chm_page.history_section.chm_history_config2 import chem_history_section_setup
from pages.chm_page.chm_reports_section import chm_report_setup
from pages.chm_page.chm_input_section import chm_input_setup
from pages.chm_page.chm_tests_section import chm_tests_setup

def chemistrySetup(self):
    self.logger.info('Entering chemistrySetup')

    chm_tests_setup(self)
    chm_input_setup(self)
    #chm_database_setup(self)
    chem_history_section_setup(self)
    chm_report_setup(self)

    # Connect the chem tab widget change function
    self.ui.chmTabWidget.currentChanged.connect(lambda index: on_chmTabWidget_currentChanged(self, index))

#TODO: reload in the data for all the sections (new data)?
def on_chmTabWidget_currentChanged(self, index):
    self.logger.info(f'Entering on_chmTabWidget_currentChanged with index: {index}')

    if(index == 0): # Database
        self.ui.headerTitle.setText('Chemistry Tests Database');
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
