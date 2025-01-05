from base_logger import logger

from PyQt5.QtWidgets import QMessageBox

def save_or_cancel_dialog(title: str, message: str):
    msgBox = QMessageBox()
    msgBox.setText(title)
    msgBox.setInformativeText(message)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
    msgBox.setDefaultButton(QMessageBox.Save)
    x = msgBox.exec_()

    if(x == QMessageBox.Save):
        return True
    if(x == QMessageBox.Cancel):
        return False

def yes_or_no_dialog(title: str, message: str):
    msgBox = QMessageBox()
    msgBox.setText(title)
    msgBox.setInformativeText(message)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.Yes)
    x = msgBox.exec_()

    if(x == QMessageBox.Yes):
        return True
    if(x == QMessageBox.No):
        return False

def yes_no_cancel_dialog(title:str, message: str):
    msgBox = QMessageBox()
    msgBox.setText(title)
    msgBox.setInformativeText(message)
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
    msgBox.setDefaultButton(QMessageBox.Yes)

    x = msgBox.exec_()

    if(x == QMessageBox.Yes):
        return True
    if(x == QMessageBox.No):
        return False
    if(x == QMessageBox.Cancel):
        return False

def okay_dialog(title: str, message: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(title)
    msg.setInformativeText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def error_dialog(title: str, message: str, detailed_msg=None):
    logger.info('Entering error_dialog with title: {title}')

    msg = QMessageBox()
    msg.setFixedWidth(400)
    msg.setIcon(QMessageBox.Information)

    msg.setText(title)
    msg.setInformativeText(message)

    if(detailed_msg):
        msg.setDetailedText(detailed_msg)

    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    msg.exec_()
