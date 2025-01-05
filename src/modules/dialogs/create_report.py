import os

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog


class CreateReport(QDialog):

    process_data = pyqtSignal(list)

    def __init__(self, parameters_manager):
        super().__init__()

        self.parameters_manager = parameters_manager

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'add_new_job.ui')
        uic.loadUi(file_path, self)

        # connect signals
        self.cancelBtn.clicked.connect(self.close)
        self.proceedBtn.clicked.connect(self.handle_proceed_btn)

        self.setup()

    def setup(self):

        int_validator = QIntValidator(0, 999999)
        decimal_validator = QDoubleValidator(0.0, 999999.99, 3)

        report_type = {
            '': None,
            'ICP': 1,
            'CHM': 2,
        }

        # set the validators for the Line Edits
        self.jobNum.setValidator(int_validator)
        self.dilution.setValidator(decimal_validator)

        # set the max lengths
        self.jobNum.setMaxLength(7)
        self.dilution.setMaxLength(10)

        for reportName, reportNum in report_type.items():
            self.reportType.addItem(reportName, reportNum)

        self.parameter.addItem('', None)
        for param_id, param_item in self.parameters_manager.get_params():
            self.parameter.addItem(param_item.param_name, param_id)


    def start(self):
        self.jobNum.clear()
        self.dilution.clear()

        self.reportType.setCurrentIndex(0)
        self.parameter.setCurrentIndex(0)


        self.exec()

    def handle_proceed_btn(self):

        jobNum = self.jobNum.text().strip()
        reportType = self.reportType.currentText()
        parameter = self.parameter.currentText()
        dilution =  self.dilution.text()

        report_id = self.reportType.currentData()
        param_id = self.parameter.currentData()

        self.process_data.emit([jobNum, report_id, param_id, dilution])



