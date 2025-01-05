from base_logger import logger

from pages.history_page.front_section.front_section_setup import front_section_setup
from pages.history_page.lab_section.lab_section_setup import lab_section_setup

#TODO: add in errors that will have to fix

def history_page_setup(self):

    front_section_setup(self)
    lab_section_setup(self)

    # set the default tab to the chem tab
    self.ui.historyTabWidget.setCurrentIndex(0)

    #TODO: load in the initial data for both

    # if change to the current page then we can load data?

   # self.ui.historyTabWidget.currentChange(lambda arguments : print(f'History Tab Section changed to {arguments}'))

def set_total_outgoing_jobs(self):
    query = '''
        SELECT count(jobNumber)
        FROM History
        WHERE status = 0
    '''
    results = self.officeDB.query(query)

    if(results):
        total = results[0][0]

        self.ui.headerDesc.setText(f'Total Outgoing Jobs: {total}')

