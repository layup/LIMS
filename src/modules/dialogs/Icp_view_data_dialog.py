import os
import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.uic import loadUi

from modules.dialogs.basic_dialogs import yes_or_no_dialog

class ViewIcpData(QDialog):

    delete_item = pyqtSignal()

    def __init__(self, icp_test_data_manager, current_item):
        super().__init__()

        self.icp_test_data_manager = icp_test_data_manager

        self.current_item = current_item

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icpViewDataDialog.ui')
        loadUi(file_path, self)

        # Connect Signals
        self.saveBtn.clicked.connect(self.handle_save)
        self.deleteBtn.clicked.connect(self.handle_delete)
        self.cancelBtn.clicked.connect(self.close)

        # set the default button
        self.saveBtn.setDefault(True)

        self.init_table()
        self.init_data()


    def init_table(self):
        headers = ['Element Symbol', 'Element Value']

        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        self.tableWidget.setColumnWidth(1, 200)

    def init_data(self):

        jobNum = str(self.current_item.jobNum)
        fileName = self.current_item.fileName
        machine = str(self.current_item.machine)
        date = self.current_item.creation

        data = self.current_item.data

        # load the preset data
        self.jobNumberLabel.setText(jobNum)
        self.textFileLabel.setText(fileName)
        self.uploadedDateLabel.setText(date)
        self.machineNumLabel.setText(machine)

        #init table
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)

        for row, (symbol, value) in enumerate(data.items()):
            print(row, symbol, value, type(value))
            element_item = QTableWidgetItem(symbol)
            element_item.setFlags(element_item.flags() & ~Qt.ItemIsEditable)

            element_value = QTableWidgetItem(str(value))

            self.tableWidget.setItem(row, 0, element_item)
            self.tableWidget.setItem(row, 1, element_value)

    def handle_save(self):
        print('Saving item')


    def handle_delete(self):
        status = yes_or_no_dialog(f'Delete {self.current_item.sampleName}', 'Are you sure you want to delete this test?')

        if(status):
            delete_status = self.icp_test_data_manager.delete_data(self.current_item.sampleName, self.current_item.machine)

            if(delete_status):
                print('Deleting Item')
                self.delete_item.emit()
                self.close()

            print('Could note delete item')
