
from PyQt5.QtWidgets import QMessageBox



def save_or_cancel_dialog(title, message):
    msgBox = QMessageBox()
    msgBox.setText(title);
    msgBox.setInformativeText(message);
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
    msgBox.setDefaultButton(QMessageBox.Save);
    x = msgBox.exec_()

    if(x == QMessageBox.Save):
        return True
    if(x == QMessageBox.Cancel):
        return False

def yes_or_no_dialog(title, message):
    msgBox = QMessageBox()
    msgBox.setText(title);
    msgBox.setInformativeText(message);
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    x = msgBox.exec_()

    if(x == QMessageBox.Yes):
        return True
    if(x == QMessageBox.No):
        return False


