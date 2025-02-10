import json

from base_logger import logger

class FilePathsManager:

    def __init__(self, file_name='default_paths.json'):

        self.file_name = file_name
        self.paths = {}

        self.setup()

    def setup(self):
        self.paths = self.load_default_paths()

        logger.info('Default Paths')
        for path_name, path in self.paths.items():
            logger.debug(f'path_name: {path_name}, path: {path}')

    def get_paths(self):
        return self.paths.items()

    def get_path(self, path_name):
        try:
            return self.paths[path_name]
        except KeyError:
            return None

    def remove_path(self, path_name):
        if path_name in self.paths:
            del self.paths[path_name]
            self.save_default_paths()


    def add_path(self, path_name, new_path):
        # Saves or update an existing path

        self.paths[path_name] = new_path

        self.save_default_paths()

    def update_paths(self, update_paths:dict):

        for key, value in update_paths.items():
            self.paths[key] = value

        self.save_default_paths()


    def load_default_paths(self):
        #logger.info('Entering load_default_paths')

        try:
            with open(self.file_name, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_default_paths(self):
        #logger.info('Entering save_default_paths')

        with open(self.file_name, 'w') as f:
            json.dump(self.paths, f, indent=4)

