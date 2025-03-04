from base_logger import logger

from PyQt5.QtWidgets import QMessageBox, QPushButton, QDialog, QLabel, QHBoxLayout, QVBoxLayout

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
    logger.info(f'Entering error_dialog with title: {title}')

    msg = QMessageBox()
    msg.setFixedWidth(400)
    msg.setIcon(QMessageBox.Information)

    msg.setText(title)
    msg.setInformativeText(message)

    if(detailed_msg):
        msg.setDetailedText(detailed_msg)

    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    msg.exec_()


def duplicate_dialog(title, message):
    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setModal(True)  # Make it modal

    layout = QVBoxLayout()

    message_label = QLabel(message)
    layout.addWidget(message_label)

    button_layout = QHBoxLayout()

    cancel_button = QPushButton("Cancel")
    overwrite_button = QPushButton("Overwrite")
    duplicate_button = QPushButton("Duplicate")

    button_layout.addWidget(cancel_button)
    button_layout.addWidget(overwrite_button)
    button_layout.addWidget(duplicate_button)

    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    overwrite_button.setDefault(True)  # Set default button

    def on_cancel():
        dialog.result = "Cancel"
        dialog.accept()

    def on_overwrite():
        dialog.result = "Overwrite"
        dialog.accept()

    def on_duplicate():
        dialog.result = "Duplicate"
        dialog.accept()

    cancel_button.clicked.connect(on_cancel)
    overwrite_button.clicked.connect(on_overwrite)
    duplicate_button.clicked.connect(on_duplicate)

    dialog.exec_()
    return getattr(dialog, 'result', None)
