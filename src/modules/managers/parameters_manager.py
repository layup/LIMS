import sqlite3

from base_logger import logger

class ParameterItem:
    def __init__(self, param_id, param_name):
        self.param_id = param_id
        self.param_name = param_name

    def get_id(self):
        return self.param_id

    def get_name(self):
        return self.param_name

    def __repr__(self):
        return f"ParameterItem(param_id={self.param_id}, param_name='{self.param_name}')"

class ParametersManager:
    def __init__(self, db):
        self.db = db

        self.parameters = {}

        self.init_setup()

    def init_setup(self):
        logger.info('Entering ParametersManager init_setup')
        parameters = self.load_params()

        if(parameters):
            for parameter in parameters:
                param_id = parameter[0]
                param_name = parameter[1]

                self.parameters[param_id] = ParameterItem(param_id, param_name)

        for key, value in self.parameters.items():
            logger.info(f'{key}: {value.__repr__}')

    def load_params(self):
        logger.info('Entering load_params')
        try:
            query = 'SELECT * FROM parameters'
            results = self.db.query(query)
            return results

        except Exception as e:
            logger.info(f'There was an error loading in the elements')
            return None

    def get_params(self):
        return self.parameters.items()

    def get_param_info(self, param_id):
        logger.info('Entering get_param_info with param_id:{param_id}')

        try:
            return self.parameters.get(param_id)
        except KeyError:
            logger.warning(f"Parameters with ID {param_id} not found.")
            return None

    def add_params(self, param_name):
        logger.info(f'Entering add_params with param_name: {param_name}')
        try:
            query = 'INSERT INTO parameters (parameterNum) values (?)'
            self.db.execute(query, (param_name, ))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                param_id = self.db.cursor.lastrowid
                logger.info(f'parameter added successfully: {param_id}')
                self.parameters[param_id] = ParameterItem(param_id, param_name)

                return param_id
            else:
                logger.warning('No parameter was insert into parameters table')
                return None

        except sqlite3.IntegrityError as e:
            logger.error(e)
            return None
        except Exception as e:
            logger.error(e)
            return None

    def remove_param(self, param_id):
        logger.info(f'Entering remove_param with param_id: {param_id}')

        try:
            query = 'DELETE FROM parameters WHERE parameterNum = ?'
            self.db.execute(query, (param_id,))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows
            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from parameters.")

                # Remove the item from the parameters
                del self.parameters[param_id]

                return deleted_rows
            else:
                logger.info("No rows were deleted (the condition may not have matched any records).")
                return None

        except sqlite3.Error as e:
            logger.info(f"Error removing {param_id} from parameters: {e}")
            return None

        except KeyError:
            logger.error("Error removing from self.parameters: {e}")
            return None

        except Exception as e:
            logger.error(f'Error: {e}')
            return None

    def update_param(self, param_id, param_name):
        logger.info(f'Entering update_param with param_id: {param_id}, param_name: {param_name}')

        try:
            # already exists in the thing
            if(param_id in self.parameters):
                query = 'UPDATE parameters SET parameterName=? WHERE parameterNum = ?'
                self.db.execute(query, (param_name, param_id, ))
                self.db.commit()
            else:
                query = 'INSERT INTO parameters (parameterName) VALUES (?)'
                self.db.execute(query, (param_name, ))
                self.db.commit()

            rows_affected = self.db.cursor.rowcount

            if rows_affected > 0:
                self.parameters[param_id] = ParameterItem(param_id, param_name)

            return rows_affected

        except sqlite3.Error as e:
            logger.error(f"Error updating icpLimits: {e}")
            return None

        except Exception as e:
            logger.error(e)
            return None

