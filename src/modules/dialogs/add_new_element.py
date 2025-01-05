import os


from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import ( QDialog, QTableWidgetItem, QTreeWidgetItem)


class addNewElementDialog(QDialog):

    status = pyqtSignal(bool)

    def __init__(self, elements_manager):
        super().__init__()

        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "ui", 'add_new_element.ui')
        uic.loadUi(file_path, self)

        self.elements_manager = elements_manager

        # Connect the buttons
        self.cancelBtn.clicked.connect(self.close)
        self.saveBtn.clicked.connect(self.handle_save_btn_clicked)

        self.error.setVisible(False)

    def handle_save_btn_clicked(self):

        errors = []

        element_name = self.name.text().lower().strip()  # Get and clean element name
        element_symbol = self.symbol.text().lower().strip()  # Get and clean element symbol

        # Validate input
        if not element_name:
            errors.append("Please enter an element name.")
        if not element_symbol:
            errors.append("Please enter an element symbol.")

        # Check for duplicate element name
        if element_name and self.elements_manager.get_element_names():
            if element_name in self.elements_manager.get_element_names():
                errors.append("An element with the same name already exists.")

        if(errors):
            # Display error messages
            error_message = '\n'.join(errors)
            self.error.setVisible(True)
            self.error.setText(error_message)
            self.status.emit(False)
            return  # Prevent further processing if there are errors

        # Add element and handle success/failure
        added_status = self.elements_manager.insert_element(element_name, element_symbol)

        if added_status:
            self.status.emit(True)
            self.close()  # Close the dialog on successful addition
        else:
            # Handle potential errors from the element manager (e.g., database issues)
            self.error.setVisible(True)
            self.error.setText("Error: Element could not be added.")
            self.status.emit(False)

