from base_logger import logger

class FrontHistoryController:

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.search_query = ''

        self.view.filterChanged.connect(self.handle_filter_change)
        self.view.searchTextEmit.connect(self.handle_search)

        self.view.nextPageClicked.connect(self.handle_next_page)
        self.view.prevPageClicked.connect(self.handle_prev_page)
        self.view.spinBoxValueChanged.connect(self.handle_spinbox_change)
        self.view.comboBoxIndexChanged.connect(self.handle_combobox_change)

        self.view.sortIndicatorChanged.connect(self.handle_sort_indicator)

        # load initial values
        self.load_initial_data()

    def load_initial_data(self):
        logger.info('Entering FrontHistoryController load_initial_data')

        # load in the initial data
        valid_rows = [50, 100, 200]

        # set the default model and footer info
        self.model.page_size = valid_rows[0]
        self.model.page_sizes = valid_rows
        self.view.footer.set_valid_rows(valid_rows)

        # load in the initial data
        data = self.model.load_items(limit=self.model.page_size , offset=self.model.off_set)
        total_pages = self.model.calculate_total_pages()

        # update database
        self.view.update_table(data)
        #self.view.footer.
        self.view.update_footer(total_pages=total_pages)

    def handle_sort_indicator(self, index):
        logger.info(f'Entering FrontHistoryController handle_sort_indicator with index: {index}')

        self.view.update_filter_index(index)

    def handle_combobox_change(self, index):
        logger.info(f'Entering FrontHistoryController handle_combobox_change with index: {index}')

        if(index != -1):
            print(f'index: {index}, new_page_size: {self.model.page_sizes[index]}')
            # update the page size
            self.model.page_size = self.model.page_sizes[index]
            # reset the current_page and offset
            self.model.current_page = 1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size

            self.update_view()

    def handle_search(self, search_query):
        logger.info(f'Entering FrontHistoryController handle_search with search_query: {search_query}')

        self.search_query = search_query
        self.model.current_page = 1;
        self.model.off_set = (self.model.current_page - 1) * self.model.page_size

        self.update_view()

    def handle_next_page(self):
        logger.info('Entering FrontHistoryController handle_next_page')

        if(self.model.current_page < self.model.total_pages):
            self.model.current_page +=1;
            self.model.off_set = (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_prev_page(self):
        logger.info('Entering FrontHistoryController handle_prev_page')

        if(self.model.current_page > 1):
            self.model.current_page -=1;
            self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
            self.update_view()

    def handle_spinbox_change(self, new_page):
        logger.info('Entering FrontHistoryController handle_spinbox_change')

        self.model.current_page = new_page;
        self.model.off_set =  (self.model.current_page - 1) * self.model.page_size
        self.update_view()


    def handle_filter_change(self, index):
        logger.info(f'Entering FrontHistoryController handle_filter_change index: {index}')

        self.view.sort_table(index)

    def update_view(self):
        logger.info('Entering update_view')

        data = self.model.load_items(limit=self.model.page_size, offset=self.model.off_set, search_query=self.search_query)
        total_pages = self.model.calculate_total_pages(search_query=self.search_query)
        self.view.update_table(data)
        self.view.update_footer(current_page=self.model.current_page, total_pages=total_pages)
