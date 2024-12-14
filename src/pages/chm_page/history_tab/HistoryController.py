
from base_logger import logger

# manages the interaction between the view and model
class HistoryController:

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.search_query = ''
        self.active_row_item = None;
        self.edit_item = None;

        self.view.filterChanged.connect(self.handle_filter_change)

        self.view.searchTextEmit.connect(self.handle_search)
        self.view.editClicked.connect(self.handle_edit_btn)
        self.view.deleteClicked.connect(self.handle_delete_btn)

        self.view.cancelBtnClicked.connect(self.handle_cancel_btn)
        self.view.saveBtnClicked.connect(self.handle_save_btn)
        self.view.nextPageClicked.connect(self.handle_next_page)
        self.view.prevPageClicked.connect(self.handle_prev_page)
        self.view.spinBoxValueChanged.connect(self.handle_spinbox_change)
        self.view.comboBoxIndexChanged.connect(self.handle_combobox_change)

        # load initial values
        self.load_initial_data()

    def load_initial_data(self):
        # load in the initial data
        valid_rows = [25, 50, 100]

        self.model.page_size = valid_rows[0]
        self.model.page_sizes = valid_rows;
        self.view.footer.set_valid_rows(valid_rows)

        # load in the initial data
        data = self.model.load_items(limit=self.model.page_size , offset=self.model.off_set)
        total_pages = self.model.calculate_total_pages()

        # update database
        self.view.update_table(data)
        self.view.update_footer(total_pages=total_pages)

    def handle_cancel_btn(self):
        logger.info('Entering handle_cancel_btn')

        self.handle_hide_side_edit()


    def handle_save_btn(self, updated_data):
        logger.info(f'Entering handle_save_btn with updated_data: {updated_data}')

        self.view.update_side_edit_visibility(False)

        update_status = self.model.update_item(self.edit_item, updated_data)

        if(update_status):
            self.view.update_table_row(self.active_row_item, self.edit_item)


    def handle_edit_btn(self, current_item, row_item):
        logger.info('Entering handle_edit_btn')

        # toggle the visibility
        self.view.update_side_edit_visibility(True)

        # save the info for what side edit is being edited
        self.edit_item = current_item
        self.active_row_item = row_item

        logger.info(current_item.__repr__())

        # load in the data to the side edit
        self.view.update_side_edit(current_item, row_item)


    def handle_delete_btn(self, current_item, row_items):
        logger.info('Entering handle_delete_btn')

        # TODO: delete model item
        self.model.remove_item(current_item)
        self.view.remove_table_row(row_items[0])

        # TODO: remove from database

        self.handle_hide_side_edit()

    def handle_combobox_change(self, index):
        logger.info(f'Entering handle_combobox_change with index: {index}')

        if(index != -1):
            print(f'index: {index}, new_page_size: {self.model.page_sizes[index]}')
            # update the page size
            self.model.page_size = self.model.page_sizes[index]
            # reset the current_page and offset
            self.model.current_page = 1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size

            self.update_view()

    def handle_search(self, search_query):
        logger.info(f'Entering handle_search with search_query: {search_query}')

        self.search_query = search_query
        self.model.current_page = 1;
        self.model.off_set = (self.model.current_page - 1) * self.model.page_size

        self.update_view()

    def handle_next_page(self):
        logger.info('Entering handle_next_page')

        if(self.model.current_page < self.model.total_pages):
            self.model.current_page +=1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_prev_page(self):
        logger.info('Entering handle_prev_page')

        if(self.model.current_page > 1):
            self.model.current_page -=1;
            self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_spinbox_change(self, new_page):
        logger.info('Entering handle_spinbox_change')

        self.model.current_page = new_page;
        self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
        self.update_view()


    def handle_filter_change(self, index):
        logger.info(f'Entering handle_filter_change index: {index}')

        self.view.sort_table(index)


    def handle_hide_side_edit(self):
        logger.info('Entering handle_hide_side_edit')

        self.view.update_side_edit_visibility(False)
        self.edit_item = None;
        self.active_row_item = None;

    def update_view(self):
        logger.info('Entering update_view')

        # toggle hide side edit
        self.handle_hide_side_edit()

        data = self.model.load_items(limit=self.model.page_size, offset=self.model.off_set, search_query=self.search_query)
        total_pages = self.model.calculate_total_pages(search_query=self.search_query)
        self.view.update_table(data)
        self.view.update_footer(current_page=self.model.current_page, total_pages=total_pages)
