
from datetime import datetime
from base_logger import logger

from PyQt5.QtCore import pyqtSignal, QObject

from modules.dialogs.text_dialog import TextFileDisplayDialog
from modules.dialogs.icp_view_data_dialog import ViewIcpDataDialog
from modules.dialogs.icp_view_job_dialog import ViewIcpJobDialog
from modules.utils.file_utils import openFile

from pages.icp_page.icp_upload import icp_upload
from pages.icp_page.history_tab.icp_history_item import IcpHistoryItem

class IcpHistoryController(QObject):

    openReport = pyqtSignal(IcpHistoryItem)

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.search_query = ''

        self.view.uploadBtnClicked.connect(self.handle_upload_btn)

        self.view.filterChanged.connect(self.handle_filter_change)
        self.view.searchTextEmit.connect(self.handle_search)
        self.view.view_sample_btn_clicked.connect(self.handle_view_sample_btn)
        self.view.view_job_btn_clicked.connect(self.handle_view_job_btn)
        self.view.printBtnClicked.connect(self.handle_print_btn)

        self.view.nextPageClicked.connect(self.handle_next_page)
        self.view.prevPageClicked.connect(self.handle_prev_page)
        self.view.spinBoxValueChanged.connect(self.handle_spinbox_change)
        self.view.comboBoxIndexChanged.connect(self.handle_combobox_change)

        self.load_initial_data()

    def load_initial_data(self):
        # load in the initial data
        valid_rows = [25, 50, 100]

        self.model.page_sizes = valid_rows

        self.view.footer.set_valid_rows(valid_rows)

        self.model.page_size = valid_rows[0]
        self.view.footer.set_limit_index(1)

        # load in the initial data
        data = self.model.load_items(limit=self.model.page_size, offset=self.model.off_set)
        total_pages = self.model.calculate_total_pages()

        # update database
        self.view.update_table(data)
        self.view.update_footer(total_pages=total_pages)

    def handle_print_btn(self, file_name):
        logger.info('Entering handle_print_btn')

        temp_file_name = 'batch_jobs.txt'
        todaysDate = datetime.today().date()

        samples = self.model.print_batch(file_name)

        with open(temp_file_name, 'w') as file:
            file.write(f'Batch Name: {file_name}\n')
            file.write(f'Date: {todaysDate}\n')
            file.write('\n')

            for sample in samples:
                file.write(f'{sample[0]} \n')

        dialog = TextFileDisplayDialog(temp_file_name)
        dialog.exec_()

    def handle_upload_btn(self):
        logger.info('Entering handle_upload_btn')

        fileLocation = openFile()
        logger.debug(f'fileLocation: {fileLocation}')
        icp_upload(fileLocation, self.model.db)

        # update the table for the data
        self.update_view()

    def handle_view_sample_btn(self, current_item):
        logger.info(f'Entering handle_view_sample_btn with current_item: {current_item}')

        dialog = ViewIcpDataDialog(self.model.icp_test_data_manager, current_item)
        #dialog.delete_item.connect(lambda self=self:handle_delete_icp_item(self))
        dialog.exec()

        #TODO: manage when delete on other pages and etc
        #TODO: fix the editing allowed feature

        self.update_view()

    def handle_view_job_btn(self, current_item):
        logger.info(f'Entering handle_view_job_btn with current_item: {current_item}')

        view_job_dialog = ViewIcpJobDialog(self.model.icp_test_data_manager, self.model.elements_manager, current_item)
        view_job_dialog.exec_()


        #self.update_view()


    def handle_filter_change(self, index):
        logger.info(f'Entering handle_filter_change index: {index}')
        self.view.sort_table(index)


    def handle_search(self, search_query):
        logger.info(f'Entering handle_search with search_query: {search_query}')

        self.search_query = search_query
        self.model.current_page = 1
        self.model.off_set = (self.model.current_page - 1) * self.model.page_size

        self.update_view()

    def handle_combobox_change(self, index):
        logger.info(f'Entering handle_combobox_change with index: {index}')

        if(index != -1):
            #print(f'index: {index}, new_page_size: {self.model.page_sizes[index]}')

            # update the page size
            self.model.page_size = self.model.page_sizes[index]

            # reset the current_page and offset
            self.model.current_page = 1
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size

            self.update_view()

    def handle_next_page(self):
        logger.info('Entering handle_next_page')

        if(self.model.current_page < self.model.total_pages):
            self.model.current_page +=1
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_prev_page(self):
        logger.info('Entering handle_prev_page')

        if(self.model.current_page > 1):
            self.model.current_page -=1
            self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_spinbox_change(self, new_page):
        logger.info('Entering handle_spinbox_change')

        self.model.current_page = new_page
        self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
        self.update_view()


    def update_view(self):
        logger.info('Entering update_view')

        data = self.model.load_items(limit=self.model.page_size, offset=self.model.off_set, search_query=self.search_query)
        total_pages = self.model.calculate_total_pages(search_query=self.search_query)
        self.view.update_table(data)
        self.view.update_footer(current_page=self.model.current_page, total_pages=total_pages)

