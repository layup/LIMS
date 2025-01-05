import json

from base_logger import logger

class FooterItem:
    def __init__(self, param_id, footer_message):
        self.param_id = param_id
        self.footer_message = footer_message

class FootersManager:
    def __init__(self, db):
        self.db = db

        self.icp_footers = {}
        self.chem_footers = {}

        self.setup()

    def setup(self):

        footers_info = self.get_all_footer_messages()

        if(footers_info):

            for footer in footers_info:
                param_id = footer[0]
                report_type = footer[1]
                footer_message = footer[2]

                if(report_type == 1):
                    self.icp_footers[param_id] = FooterItem(param_id, footer_message)

                if(report_type == 2):
                    self.chem_footers[param_id] = FooterItem(param_id, footer_message)

    def get_icp_footers(self):
        return self.icp_footers.items()

    def get_chem_footers(self):
        return self.chem_footers.items()

    def get_footer_message(self, param_id, report_type):
        logger.info('Entering get_footer_message with param_id: {param_id}, report_type: {report_type}')

        if(report_type == 1):
            if(param_id in self.icp_footers):
                return self.icp_footers[param_id].footer_message
            return None

        if(report_type == 2):
            if(param_id in self.chem_footers):
                return self.chem_footers[param_id].footer_message
            return None


    def get_all_footer_messages(self):
        logger.info('Entering get_all_footer_messages')

        try:
            query = 'SELECT * FROM Footers'
            results = self.db.query(query)
            return results

        except Exception as e:
            logger.error(f'Error loading authors: {e}')
            return None

    def get_footer(self, param_id, report_type):
        logger.info(f'Entering get_footer with param_id: {param_id}, report_type: {report_type}')

        try:
            query = 'SELECT * FROM Footers WHERE param_id = ? AND report_type = ?'
            results = self.db.query(query, (param_id, report_type))
            return results

        except Exception as e:
            logger.error(f'Error loading authors: {e}')
            return None

    def add_footers(self, param_id, report_type, footer_message):
        logger.info(f'Entering add_footers with param_id: {param_id}, report_type: {report_type}')

        try:
            query = 'INSERT OR REPLACE INTO Footers (param_id, report_type, footer_message) VALUES (?, ?, ?)'

            self.db.execute(query, (param_id, report_type, footer_message))
            self.db.commit()

            if(self.db.cursor.rowcount > 0):
                logger.info('Footer was successfully updated')

                if(report_type == 1):
                    self.icp_footers[param_id] = FooterItem(param_id, footer_message)
                if(report_type == 2):
                    self.chem_footers[param_id] = FooterItem(param_id, footer_message)

                return param_id

            else:
                logger.warning("No footer was inserted.")
                return None

        except Exception as e:
            logger.info(f'Error adding footer: {e}')
            return None