
from pages.icp_page.element_tab.icp_elements_config import icp_elements_setup
from pages.icp_page.history_tab.icp_history_config import icp_history_setup
from pages.icp_page.report_tab.icp_reports_config import icp_report_section_setup


def icp_setup(self):
    self.logger.info('Entering icpSetup')

    icp_history_setup(self)
    icp_elements_setup(self)
    icp_report_section_setup(self)

    # Connect signal
    self.ui.icpTabWidget.currentChanged.connect(lambda index: on_icpTabWidget_currentChanged(self, index))

def on_icpTabWidget_currentChanged(self, index):
    self.logger.info(f'Entering on_icpTabWidget_currentChanged with index: {index}')

    if(index == 0): # History
        self.ui.headerTitle.setText('ICP Database')
        self.ui.headerDesc.setText('')

    if(index == 1): # Elements Info
        self.ui.headerTitle.setText('ICP Elements Information')

        totalElements = self.elements_manager.get_total_elements()
        self.ui.headerDesc.setText(f"Total Defined Elements: {totalElements}")

    if(index == 2): # Reports Info
        self.ui.headerTitle.setText('ICP Reports Information')
        self.ui.headerDesc.setText('')

