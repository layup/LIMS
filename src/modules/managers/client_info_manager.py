from base_logger import logger

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QWidget

class ClientInfoManager(QObject):

    def __init__(self, client_widget):
        super().__init__()
        self.client_widget = client_widget

        # Define a dictionary that maps the field names to the widget names
        self.client_info_mapping = {
            'clientName': 'clientName_1',
            'date': 'date_1',
            'time': 'time_1',
            'attn': 'attention_1',
            'addy1': 'addy1_1',
            'addy2': 'addy2_1',
            'addy3': 'addy3_1',
            'sampleType1': 'sampleType1_1',
            'sampleType2': 'sampleType2_1',
            'totalSamples': 'totalSamples_1',
            'recvTemp': 'recvTemp_1',
            'tel': 'tel_1',
            'email': 'email_1',
            'fax': 'fax_1',
            'payment': 'payment_1',
        }

        # Initialize the data dictionary to store values
        self.client_info_data = {
            'clientName': '',
            'date': '',
            'time': '',
            'attn': '',
            'addy1': '',
            'addy2': '',
            'addy3': '',
            'sampleType1': '',
            'sampleType2': '',
            'totalSamples': '',
            'recvTemp': '',
            'tel': '',
            'email': '',
            'fax': '',
            'payment': ''
        }

        # Dynamically find the widgets and store their references
        self.widgets = {}

        for field, widget_name in self.client_info_mapping.items():
            widget = self.client_widget.findChild(QLineEdit, widget_name)
            if widget:
                self.widgets[field] = widget
                # Connect the textChanged signal to update the dictionary
                widget.textChanged.connect(lambda text, field=field: self.update_client_info(field, text))

    def get_client_info(self):
        """Return the dictionary containing all the client information."""
        print(self.client_info_data)
        return self.client_info_data

    def print_child_widgets(self):
        print('print_child_widgets')

        for child in self.client_widget.findChildren(QWidget):
            widget_name = child.objectName() or "(no name)"
            widget_type = type(child).__name__
            print(f"Widget Name: {widget_name}, Widget Type: {widget_type}")

    def update_client_info(self, field_name, text):
        """Update the dictionary with the new value."""
        self.client_info_data[field_name] = text
        logger.info(f"Updated {field_name}: {text}")