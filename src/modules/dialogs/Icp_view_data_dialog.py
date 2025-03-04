import os
import json

from base_logger import logger

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.uic import loadUi

from modules.dialogs.basic_dialogs import yes_or_no_dialog, okay_dialog

class ViewIcpDataDialog(QDialog):

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
            #print(row, symbol, value, type(value))
            element_item = QTableWidgetItem(symbol)
            element_item.setFlags(element_item.flags() & ~Qt.ItemIsEditable)

            element_value = QTableWidgetItem(str(value))

            self.tableWidget.setItem(row, 0, element_item)
            self.tableWidget.setItem(row, 1, element_value)

    def handle_save(self):

        new_job_num = self.jobNumberLabel.text()
        current_job_num = str(self.current_item.jobNum)

        current_machine = self.current_item.machine

        # package the data here
        packaged_data = self.package_data()

        logger.info(f'packaged_data: {packaged_data}' )

        if(new_job_num != current_job_num):
            _, sample_num = self.current_item.sampleName.split('-')
            new_sample_name = f'{new_job_num}-{sample_num}'

            check_status = self.icp_test_data_manager.get_data(new_sample_name, current_machine)

            title = f'Update Job Number from {current_job_num} to {new_job_num}'
            message = f'Renaming {self.current_item.sampleName} to {new_sample_name} will '

            if(check_status):
                message += "overwrite the existing sample with that name. Are you sure you want to proceed?"
            else:
                message += "create a new sample. Are you sure you want to proceed?"

            response = yes_or_no_dialog(title, message)

            if(response):
                # delete our previous data
                self.icp_test_data_manager.delete_data(self.current_item.sampleName, current_machine)

                if(check_status):
                    # update the existing new thing
                    status = self.icp_test_data_manager.update_data(new_sample_name, current_machine, packaged_data)

                else:
                    # add a new test item
                    status = self.icp_test_data_manager.add_data(new_sample_name, int(new_job_num), self.current_item.fileName, packaged_data, current_machine)

            return


        status = self.icp_test_data_manager.update_data(self.current_item.sampleName, current_machine, packaged_data)

        if(status):
            okay_dialog(f'Successfully saved {self.current_item.jobNum}', '')

    def package_data(self):

        data = {}

        for row in range(self.tableWidget.rowCount()):
            element_symbol = self.tableWidget.item(row, 0).text()
            element_value = self.tableWidget.item(row, 1).text()

            data[element_symbol] = element_value

        return json.dumps(data)


    def handle_delete(self):
        status = yes_or_no_dialog(f'Delete {self.current_item.sampleName}', 'Are you sure you want to delete this test?')

        if(status):
            delete_status = self.icp_test_data_manager.delete_data(self.current_item.sampleName, self.current_item.machine)

            if(delete_status):
                print('Deleting Item')
                self.delete_item.emit()
                self.close()

            print('Could note delete item')
