
from base_logger import logger

from modules.dbFunctions import updateHistoryStatus
from pages.history_page.HistoryItem import HistoryItem

class HistoryManager:
    def __init__(self, database):
        self.db = database
        self.history_items = []

        self.outgoing_items = []

    def add_item(self, jobNum, companyDate, creationDate, status):
        self.history_items.append(HistoryItem(jobNum, companyDate, creationDate, status))

    def load_data(self, limit, offset):
        history_data = getHistoryData4(self.db, limit, offset)

        for current_data in history_data:
            # Unpack the current_data directly into jobNum, companyDate, creationDate, and status
            jobNum, companyDate, creationDate, status = current_data
            self.add_item(jobNum, companyDate, creationDate, status)

    def toggle_item_status(self, index):
        if 0 <= index < len(self.history_items):
            current_item = self.history_items[index]
            jobNum = current_item.jobNum
            new_status = current_item.toggle_status()  # Toggle and return new status

            updateHistoryStatus(self.db, jobNum, new_status)

            return new_status
        return None

    def update_database(self):
        pass;

    def total_items(self):
        return len(self.history_items)

    def get_all_items(self):
        return self.history_items

    def clear_items(self):
        self.history_items.clear()

    def filter_search(self, search_term, limit, offset):
        logger.info(f'Entering filter_search with parameters: search_term: {search_term}, limit: {limit}, offset: {offset}')
        filtered_data = search_jobs(self.db, search_term, limit, offset)

        if(len(filtered_data) == 0):
            self.history_items = []
            return 0;

        for current_data in filtered_data:
            # Unpack the current_data directly into jobNum, companyDate, creationDate, and status
            jobNum, companyDate, creationDate, status = current_data
            logger.debug(f'current_data: {current_data}')
            self.add_item(jobNum, companyDate, creationDate, status)

        return len(filtered_data)

    def print_all_items(self):
        for item in self.history_items:
            print(f'jobNum: {item.jobNum}, status: {item.status}')


def getHistoryData4(db, limit, offset):
    query = 'SELECT jobNumber, companyName, creationDate, status FROM History ORDER BY creationDate DESC LIMIT ? OFFSET ?'
    results = db.query(query, (limit, offset))
    return results

def search_jobs(db, search_term, limit, offset):
    query = """
        SELECT jobNumber, companyName, creationDate, status
        FROM History
        WHERE jobNumber LIKE ? OR companyName LIKE ?
        ORDER BY creationDate DESC
        LIMIT ? OFFSET ?
    """

    # Add wildcards to the search term for partial matching
    search_term = f"{search_term}%"

    # Execute the query with the search term and pagination parameters
    results = db.query(query, (search_term, search_term, limit, offset))

    return results
