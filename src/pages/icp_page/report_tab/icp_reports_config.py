from base_logger import logger

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QListWidgetItem

from modules.dialogs.basic_dialogs import okay_dialog

#******************************************************************
#    ICP Reports
#******************************************************************

def icp_report_section_setup(self):

    load_parameters(self)

    # Connect Signals
    self.ui.reportsList.itemSelectionChanged.connect(lambda: handle_param_item_selected(self))
    self.ui.icpReportCancelBtn.clicked.connect(lambda: handle_cancel_btn_clicked(self))
    self.ui.saveFooterBtn.clicked.connect(lambda: handle_save_btn_clicked(self))

def load_parameters(self):

    for param_id, param_item in self.parameters_manager.get_params():
        list_item = QListWidgetItem(param_item.param_name)
        list_item.setData(Qt.UserRole, param_id)

        self.ui.reportsList.addItem(list_item)

def handle_param_item_selected(self):

    selected_item = self.ui.reportsList.currentItem()

    if selected_item:
        param_name = selected_item.text()
        param_id = selected_item.data(Qt.UserRole)

        # Set the report Name Label
        self.ui.icpReportNameLabel.setText(f'[{param_id}] {param_name.upper()}')

        load_icp_footer_message(self, param_id)

def load_icp_footer_message(self, param_id, report_type=1):

    self.ui.footerComments.clear()

    footer_comment = self.footers_manager.get_footer_message(param_id, report_type)

    if(footer_comment):
        self.ui.footerComments.setPlainText(footer_comment)

@pyqtSlot()
def handle_cancel_btn_clicked(self):

    selected_param = self.ui.reportsList.currentItem()

    if selected_param:
        param_id = selected_param.data(Qt.UserRole)

        load_icp_footer_message(self, param_id)

@pyqtSlot()
def handle_save_btn_clicked(self):

    footer_comment = self.ui.footerComments.toPlainText()
    selected_param = self.ui.reportsList.currentItem()
    report_type = 1

    if(selected_param and footer_comment):
        param_id = selected_param.data(Qt.UserRole)

        status = self.footers_manager.add_footers(param_id, report_type, footer_comment)

        if(status):
            okay_dialog('ICP Report Comment Saved', '')
