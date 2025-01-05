import os
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.uic import loadUi



class ViewIcpData(QDialog):
    def __init__(self, db, current_item):
        super().__init__()

        self.db =db
        self.current_item = current_item

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icpViewDataDialog.ui')
        loadUi(file_path, self)

        # Connect Signals
        self.saveBtn.clicked.connect(lambda: print('save button clicked'))
        self.cancelBtn.clicked.connect(self.close)

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
        pass;


class viewIcpDataDialog(QDialog):

    def __init__(self, db, sampleNum,  machineType):
        super().__init__()

        self.db = db
        self.sampleNum = sampleNum
        self.jobNum = sampleNum[0:6]
        self.machineType = machineType

        # load UI
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'icpViewDataDialog.ui')
        loadUi(file_path, self)

        # Connect Signals
        self.saveBtn.clicked.connect(lambda: print('save button clicked'))
        self.cancelBtn.clicked.connect(self.close)

        self.init_data()

    def init_data(self):
        # Get the data from the database
        query = f"SELECT * FROM icpData WHERE jobNum = '{self.jobNum}' AND machineNum = '{int(self.machineType)}'"
        results = self.db.query(query)

        fileName = results[0][2]
        uploadDate = results[0][4]
        sampleNames = [item[0] for item in results]
        sampleNames.insert(0, 'Elements')
        elementNames = list(json.loads(results[0][3]).keys())

        # Lod the preset data
        self.jobNumberLabel.setText(self.jobNum)
        self.textFileLabel.setText(fileName)
        self.uploadedDateLabel.setText(uploadDate)
        self.machineNumLabel.setText(str(self.machineType))

        # Prepare the table
        self.tableWidget.setRowCount(len(elementNames))
        self.tableWidget.setColumnCount(len(sampleNames))
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)

        # Set the table headers
        self.tableWidget.setHorizontalHeaderLabels(sampleNames)

        # Assign elements row and disable editing of them
        for row, element in enumerate(elementNames):
            item = QTableWidgetItem(element)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 0, item)

        for col, data in enumerate(results, start=1):

            if isinstance(data[3], str):  # Check if it's a string
                try:
                    element_data = json.loads(data[3])  # Load JSON into a dictionary

                    for row, (key, value) in enumerate(element_data.items()):
                        #print(f'col: {col}, row: {row}, key: {key} data: {value}')
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, value)
                        self.tableWidget.setItem(row, col, item)

                except json.JSONDecodeError:
                    print("Error: Invalid JSON data")  # Handle potential invalid JSON