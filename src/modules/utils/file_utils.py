import os
import re
import json

from base_logger import logger
from dotenv import load_dotenv, dotenv_values

from PyQt5.QtWidgets import QFileDialog


def update_env_file(key, value):

    # load existing .env files
    config = dotenv_values('.env')

    # update the values
    config[key] = value

    # 'w' overwrites the entire file
    with open('.env', 'w') as f:
        for key, value in config.items():
            f.write(f'{key}={value}\n')


def openFile():
    logger.info('Entering openFile')
    fileName, _ = QFileDialog.getOpenFileName(None, 'Open File', '',)
    print(f'fileName: {fileName}')
    return fileName

def getFileLocation():
    logger.info('Entering getFileLocation')
    dlg = QFileDialog().getExistingDirectory()
    print(f'dlg: {dlg}')
    return dlg

def determineFileType(file_path):

    return os.path.splitext(file_path)[1]

def scanDir(path):
    logger.info(f'Entering ScanDir with parameter path: {path}')

    obj = os.scandir(path)
    #file = os.listdir(path)

    for entry in obj :
        if entry.is_dir() or entry.is_file():
            print(entry.name)

    obj.close()

def get_path_from_json(filename, key):
    logger.info(f'Entering get_path_from_json with filename: {filename}, key: {key}')

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get(key)  # Use get() to avoid KeyError if key is not found

    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None  # Handle invalid JSON data

def scan_for_txt_folders(jobNum):
    logger.info(f'Entering scan_for_txt_folders with parameter jobNum: {jobNum}')

    text_folders_path = get_path_from_json('default_paths.json','TXTDirLocation')

    locationsObject = os.scandir(text_folders_path)

    text_folder_paths = []

    for entry in locationsObject:
        if(entry.is_dir()):
            if(re.match('^TXT-[a-zA-Z]{3}$', entry.name)):
                text_folder_paths.append(os.path.join(text_folders_path, entry.name))

    locationsObject.close()

    return process_txt_folders(jobNum, text_folder_paths)


def process_txt_folders(jobNum, text_folder_paths):
    logger.info(f'Entering process_txt_folders with parameter jobNum: {jobNum}, text_folder_paths: {text_folder_paths}')

    file_name = f"W{jobNum}.TXT"

    for location in text_folder_paths:
        temp_location_object = os.scandir(location)

        for entry in temp_location_object:
            if(entry.is_file() and re.match(file_name, entry.name)):
                temp_location_object.close()

                return os.path.join(location, entry.name)

        temp_location_object.close()

    return None
