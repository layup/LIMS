import os

from PyQt5.QtCore import (Qt, pyqtSignal, QObject)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem
from PyQt5.uic import loadUi


class SideEditWidget2(QWidget):

    cancel_clicked = pyqtSignal(bool)
    save_clicked = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.row_item_list = None;
        self.model_item = None;

        # Load UI elements
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'chmTestsEditSideWidget.ui')

        self.ui = loadUi(file_path, self)

        # Load general setup
        self.init_setup()


    def init_setup(self):

        # allow only float values
        float_validator = QDoubleValidator()
        float_validator.setDecimals(10)

        # allow only int values
        int_validator = QIntValidator()

        # Set validators
        self.jobNum.setValidator(int_validator)
        self.sampleNum.setValidator(int_validator)
        self.testsVal.setValidator(float_validator)
        self.standard.setValidator(float_validator)

        # set the limit to characters allowed in line edit
        self.jobNum.setMaxLength(6)
        self.sampleNum.setMaxLength(6)
        self.testsVal.setMaxLength(30)


    def loads_tests(self, tests, units):

        # clear of all existing items
        self.testsNameCombo.clear()
        self.unitValCombo.clear()


        for test_item in tests:
            test_id = test_item.test_id
            test_name = test_item.test_name

            self.testsNameCombo.addItem(test_name)
            index = self.testsNameCombo.count() -1
            self.testsNameCombo.setItemData(index, test_id)


        self.unitValCombo.addItems(units)

    def set_tests_index(self, testNum):
        for index in range(self.testsNameCombo.count()):
            item_testNum = self.testsNameCombo.itemData(index)  # Get the data stored for each item
            if item_testNum == testNum:
                self.testsNameCombo.setCurrentIndex(index)  # Set the combo box to this index
                return

        #TODO: couldn't find it

    def on_test_selected(self, index):
        selected_testNum = self.testsNameCombo.itemData(index)
        return selected_testNum

    def load_job_info(self, model_item, row_item_list):

        self.jobNum.setText(str(model_item.jobNum))
        self.sampleNum.setText(str(model_item.sampleNum))

        self.jobNum.setReadOnly(True)
        self.sampleNum.setReadOnly(True)

        self.testsVal.setText(str(model_item.testVal))
        self.standard.setText(str(model_item.standard))

        self.set_tests_index(model_item.testNum)
        self.unitValCombo.setCurrentText(model_item.unit)

        self.testsNameCombo.setEnabled(False)

        self.row_item_list = row_item_list
        self.model_item = model_item

    def get_job_info(self):

        current_index = self.testsNameCombo.currentIndex()
        testNum = self.testsNameCombo.itemData(current_index)
        testVal = self.testsVal.text()
        standard = self.standard.text()
        unit = self.unitValCombo.currentText()

        return [testNum, testVal, standard, unit]


class SideEditWidget(QWidget):

    cancel_clicked = pyqtSignal(bool)
    save_clicked = pyqtSignal(list, object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.item = None;
        self.disabled = False;
        self.input_data = None;

        # Load UI elements
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'chmTestsEditSideWidget.ui')

        self.ui = loadUi(file_path, self)

        # Load general setup
        self.init_setup()

        # Connect signals
        self.saveBtn.clicked.connect(self.on_save_clicked)

    def init_setup(self):

        # allow only float values
        float_validator = QDoubleValidator()
        float_validator.setDecimals(10)

        # allow only int values
        int_validator = QIntValidator()

        # Set validators
        self.jobNum.setValidator(int_validator)
        self.sampleNum.setValidator(int_validator)
        self.testsVal.setValidator(float_validator)
        self.standard.setValidator(float_validator)

        # set the limit to characters allowed in line edit
        self.jobNum.setMaxLength(6)
        self.sampleNum.setMaxLength(6)
        self.testsVal.setMaxLength(30)

    def set_drop_down(self, parameterTypes, unitTypes):
        for item in parameterTypes:

            self.testsNameCombo.addItem(item.test_name, userData=item.test_id)

        self.unitValCombo.addItems(unitTypes)


    def set_primary_key_editable(self, status:bool):
        self.jobNum.setReadOnly(not status)
        self.sampleNum.setReadOnly(not status)
        self.testsNameCombo.setEditable(not status)


    def set_data(self, data):

        self.input_data = data;

        self.jobNum.setText(data[0])
        self.sampleNum.setText(data[1])
        self.testsVal.setText(data[3])
        self.standard.setText(data[5])

        self.set_combo_widget(self.testsNameCombo, data[2])
        self.set_combo_widget(self.unitValCombo, data[4])

        # enable/disable combobox editing
        self.testsNameCombo.setDisabled(self.disabled)
        #self.unitValCombo.setDisabled(self.disabled)


    def set_combo_widget(self, widget, itemName):
        try:
            index = widget.findText(itemName)

            if(index != -1):
                widget.setCurrentIndex(index)

        except Exception as e:
            print(e)

    def get_data(self):
        jobNum = self.jobNum.text()
        sampleNum = self.sampleNum.text()
        testsName = self.testsNameCombo.currentText()
        testsVal = self.testsVal.text()
        standardVal = self.standard.text()
        unitVal = self.unitValCombo.currentText()

        index = self.testsNameCombo.currentIndex()
        testNum = str(self.testsNameCombo.itemData(index, role=Qt.UserRole))

        return [jobNum, sampleNum, testsName, testsVal, unitVal, standardVal, testNum]

    def clear_data(self):
        self.jobNum.clear()
        self.sampleNum.clear()
        self.testsVal.clear()
        self.standard.clear()

    def set_combo_disabled(self, status:bool):
        self.disabled = status;

    def set_item(self, item):
        self.item = item

    def get_item(self):
        return self.item

    def on_save_clicked(self):
        result = self.get_data()
        #self.save_clicked.emit(result, self.current_row)

        self.save_clicked.emit(result, self.item);


def hideSideEditWidget(widget):

    # Clear the data
    widget.clear_data()

    # set not visible
    widget.setVisible(False)

def getParameterTypeNum(comboBox):

    index = comboBox.currentIndex()

    item = comboBox.itemData(index)

    return str(item.testNum)
