
from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from modules.dialogs.tests_item_dialog import TestsItemDialog
from modules.dialogs.basic_dialogs import yes_or_no_dialog

class TestsController(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.model = model
        self.view = view

        self.search_query = ''

        self.view.edit_btn_clicked.connect(self.handle_edit_btn)
        self.view.delete_btn_clicked.connect(self.handle_delete_btn)
        self.view.add_btn_clicked.connect(self.handle_add_btn)
        self.view.search_btn_clicked.connect(self.handle_search_btn)
        self.view.clear_btn_clicked.connect(self.handle_clear_btn)
        self.view.test_selected.connect(self.handle_test_selected)

        self.load_init_data()

    def load_init_data(self):

        self.load_data()

    def load_data(self):
        tests = self.model.get_tests_type('C')
        self.view.update_tree(tests)
        self.view.update_table(tests)


    def handle_test_selected(self, item):
        logger.info('Entering handle_test_selected')

        test_id = item.text(0)
        test_name = item.text(1)

        logger.info(f'test_id: {test_id}, test_name: {test_name}')


    def handle_edit_btn(self, test_id):
        logger.info(f'Entering handle_edit_btn with test_id: {test_id}')

        test_data = self.model.get_chem_tests_info(test_id)

        if(test_data):

            item = TestsItemDialog('Update Tests', test_id, test_data)
            #item.new_data.connect(self.model.add_new_chem_tests(self.model.))
            item.exec()

    def handle_delete_btn(self, test_id):
        logger.info(f'Entering handle_delete_btn with test_id: {test_id}')

        status = yes_or_no_dialog('Confirm Deletion?', f'Are you sure you want to delete test with ID {test_id}?\nThis action cannot be undone.')

        if(status):
            remove_status = self.model.remove_test(test_id)

            if(remove_status):
                self.load_data()

    def handle_add_btn(self):
        logger.info('Entering handle_add_btn')

        item = TestsItemDialog('Add New Tests')
        item.new_data.connect(self.model.add_new_chem_tests())

        item.exec()

    def handle_clear_btn(self):
        logger.info('Entering handle_clear_btn')
        self.load_data()

    def handle_search_btn(self):
        logger.info('Entering handle_search_btn')

        current_text = self.view.search_bar.text()

        logger.debug(f'current_text: {current_text}')

        if(current_text):
            tests = self.model.get_search_tests(current_text, 'C')
            self.view.update_table(tests)
            return

        self.load_data()






