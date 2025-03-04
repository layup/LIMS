
import sqlite3

from base_logger import logger

class ElementLimits:

    def __init__(self, param_id, unit, lower_limit, upper_limit, side_comment, footer_comment):
        self.param_id = param_id
        self.unit = unit
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.side_comment = side_comment
        self.footer_comment = footer_comment

    def __repr__(self):
        return f"ElementLimits(param_id={self.param_id}, unit='{self.unit}', " \
               f"lower_limit={self.lower_limit}, upper_limit={self.upper_limit}, " \
               f"side_comment='{self.side_comment}, footer_comment={self.footer_comment}')"

class ElementItem:
    def __init__(self, element_id, name, symbol):
        self.element_id = element_id
        self.name = name
        self.symbol = symbol

        self.limits = {}

    def get_limits(self, param_id):

        if(param_id in self.limits):
            return self.limits[param_id]

        return None

    def __repr__(self):
        # Include all attributes, even optional ones (with checks for None)
        limits_repr = f"limits={self.limits!r}" if self.limits else "limits=None"
        return f"ElementItem(element_id={self.element_id}, name='{self.name}', symbol='{self.symbol}', {limits_repr})"

class ElementsManager:

    def __init__(self, db):
        self.db = db
        self.elements = {}

        self.init_setup()

    def init_setup(self):
        logger.info('Entering ElementsManager init_setup')

        elements = self.load_all_elements()

        if not elements:
            return

        # Define the core elements and basic information
        for element_id, element_name, element_symbol in elements:
            self.elements[element_id] = ElementItem(element_id, element_name, element_symbol)

         # Once basic information is loaded in then load the limits
        for element_id, element_item in self.elements.items():
            limits = self.load_element_limit(element_id)

            if not limits:
                continue

            for param_id, _ , unit_type, lower_limit, upper_limit, side_comment, footer_comment in limits:
                element_item.limits[param_id] = ElementLimits(param_id, unit_type, lower_limit, upper_limit, side_comment, footer_comment)

        for key, value in self.elements.items():
            logger.info(f'{key}: {value.__repr__}')

    def load_all_elements(self):
        try:
            query = 'SELECT * FROM icp_elements ORDER BY element_name ASC'
            results = self.db.query(query)
            return results

        except Exception as e:
            logger.info(f'There was an error loading in the icp_elements: {e}')
            return None

    def load_element_limit(self, element_id):
        try:
            query = 'SELECT * FROM icp_limits WHERE element_id = ?'
            results = self.db.query(query, (element_id,))
            return results

        except Exception as e:
            logger.info(f'There was an error loading limit for element with id:{element_id}: {e}')
            return None

    def remove_element(self, element_id):
        logger.info('Entering remove_element with element_id: {element_id}')
        if(element_id in self.elements):
            pass;


    def get_total_elements(self):
        return len(self.elements)

    def get_elements(self):
        return self.elements

    def get_element_symbols(self):

        symbol_list = []

        for element_id, element_item in self.elements.items():
            symbol_list.append(element_item.symbol)

        return symbol_list


    def get_element_names(self):

        element_name = []

        for element_id, element_item in self.elements.items():
            element_name.append(element_item.name)

        return element_name


    def get_element_info(self, element_id):

        if(element_id in self.elements):
            return self.elements[element_id]

        return None

    def get_limits_item(self, element_id, param_id):

        if(element_id in self.elements):
            return self.elements[element_id].get_limits(param_id)

        return None

    def delete_element(self, element_id):
        logger.info(f'Entering delete_element with element_id: {element_id}')

        try:
            query = 'DELETE FROM icp_elements WHERE element_id = ?'
            self.db.execute(query, (element_id,))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows
            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from icp_elements.")

                # Remove the item from the parameters
                del self.elements[element_id]

                return deleted_rows
            else:
                logger.info("No rows were deleted (the condition may not have matched any records).")
                return None

        except sqlite3.Error as e:
            logger.info(f"Error removing {element_id} from icp_elements: {e}")
            return None

        except KeyError:
            logger.error("Error removing from self.elements: {e}")
            return None

        except Exception as e:
            logger.error(f'Error: {e}')
            return None

    def insert_element(self, name, symbol):
        logger.info(f'Entering insert_element with name: {name}, symbol: {symbol}')

        try:
            query = 'INSERT INTO icp_elements (element_name, element_symbol) VALUES (?, ?)'
            self.db.execute(query, (name, symbol))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                element_id = self.db.cursor.lastrowid
                self.elements[element_id] = ElementItem(element_id, name, symbol)
                logger.info(f'Element added successfully: {element_id}')
                return element_id

            logger.warning('No element was insert into elements table')
            return None

        except sqlite3.IntegrityError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(e)
            return None

    def update_element(self, element_id, name, symbol):
        logger.info(f'Entering update_element with element_id: {element_id}, symbol: {symbol}, name: {name}')

        try:
            if(element_id in self.elements):

                query = 'UPDATE icp_elements SET element_name = ?, element_symbol = ? WHERE  element_id=?'
                self.db.execute(query, (name, symbol, element_id))
                self.db.commit()

                rows_affected = self.db.cursor.rowcount

                if rows_affected > 0:
                    self.elements[element_id].name = name
                    self.elements[element_id].symbol = symbol

                    logger.info(f'Element successfully updated: {element_id}')
                    return rows_affected

            logger.warning(f'could not updated element: {element_id} since not in self.elements')
            return None

        except sqlite3.Error as e:
            logger.error(f'{e}')
            return None

        except Exception as e:
            logger.error(f'{e}')
            return None

    def insert_or_update_limits(self, param_id, element_id, unit_type, lower_limit, upper_limit, side_comment, footer):
        logger.info(f"Entering insert_or_update_limits with arguments: "
                    f"param_id={param_id}, element_id={element_id}, "
                    f"unit_type='{unit_type}', lower_limit={lower_limit}, "
                    f"upper_limit={upper_limit}, side_comment='{side_comment}'"
                    f"footer={footer}")

        try:
            if(element_id in self.elements):
                if param_id in self.elements[element_id].limits:
                    # already exists so just update
                    query = 'UPDATE icp_limits SET unit_name=?, lower_limit=?, upper_limit=?, side_comment=?, footer_comment=? WHERE param_id=? AND element_id=?'
                    self.db.execute(query, (unit_type, lower_limit, upper_limit, side_comment, footer,  param_id, element_id, ))
                    self.db.commit()

                else:
                    # doesn't already exist so create the thing
                    query = 'INSERT INTO icp_limits (param_id, element_id, unit_name, lower_limit, upper_limit, side_comment, footer_comment) VALUES (?, ?, ?, ?, ?, ?)'
                    self.db.execute(query, (param_id, element_id, unit_type, lower_limit, upper_limit, side_comment, footer, ))
                    self.db.commit()

                rows_affected = self.db.cursor.rowcount

                if rows_affected > 0:
                    self.elements[element_id].limits[param_id] = ElementLimits(param_id, unit_type, lower_limit, upper_limit, side_comment, footer)

                return rows_affected

        except sqlite3.Error as e:
            logger.error(f"Error updating icp_limits: {e}")
            return None

        except Exception as e:
            logger.error(e)
            return None

