
from base_logger import logger

from modules.dialogs.basic_dialogs import error_dialog


class EmptyDataTableError(Exception):
    pass

def validate_excel_creation_data(author_names: list, sample_names: list, client_info:dict):

    try:

        if(len(author_names) == 0):
            raise ValueError('At least one author must be selected.')

        for sample_id, sample_name in sample_names.items():
            if(sample_name == ''):
                raise ValueError(f'In the Client Info Section {sample_id} does not have sample name associated, please enter a name')

        # check if the table data is empty and if they want to create an empty table

        return True

    except ValueError as e:
        logger.error(str(e))
        error_dialog('Excel Creation Data Error', str(e))

        return False

    except Exception as e:
        logger.error(f'Unexpected error during excel data validation {e}')
        return False
