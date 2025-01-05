
from base_logger import logger

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QListWidgetItem

from modules.dialogs.basic_dialogs import okay_dialog

#******************************************************************
#    Chemistry Report Info
#******************************************************************
def chm_reports_tab_setup(self):
    logger.info('Entering chm_reports_tab_setup')

    # Load the init data on the setup
    load_parameter_types(self)

    # Connect Report signals
    self.ui.chmReportList.itemSelectionChanged.connect(lambda: handle_param_item_selected(self))
    self.ui.chmReportCancelBtn.clicked.connect(lambda: handle_cancel_btn_clicked(self))
    self.ui.chmReportSaveBtn.clicked.connect(lambda: handle_save_btn_clicked(self))

def load_parameter_types(self):

    for param_id, param_item in self.parameters_manager.get_params():
        list_item = QListWidgetItem(param_item.param_name)
        list_item.setData(Qt.UserRole, param_id)

        self.ui.chmReportList.addItem(list_item)

def handle_param_item_selected(self):

    selected_param = self.ui.chmReportList.currentItem()

    if selected_param:
        param_name = selected_param.text()
        param_id = selected_param.data(Qt.UserRole)

        self.ui.chmReportNameLabel.setText(f'[{param_id}] {param_name.upper()}')

        load_chm_footer_message(self, param_id)

def load_chm_footer_message(self, param_id, report_type=2):

    self.ui.chmFooterComment.clear()

    footer_comment = self.footers_manager.get_footer_message(param_id, report_type)

    if(footer_comment):
        self.ui.chmFooterComment.setPlainText(footer_comment)

@pyqtSlot()
def handle_cancel_btn_clicked(self):

    selected_item = self.ui.chmReportList.currentItem()

    if(selected_item):
        param_id = selected_item.data(Qt.UserRole)

        load_chm_footer_message(self, param_id)

@pyqtSlot()
def handle_save_btn_clicked(self):

    footer_comment = self.ui.chmFooterComment.toPlainText()
    selected_param = self.ui.chmReportList.currentItem()
    report_type = 2

    if(selected_param and footer_comment):
        param_id = selected_param.data(Qt.UserRole)

        status = self.footers_manager.add_footers(param_id, report_type, footer_comment)

        if(status):
            okay_dialog('CHM Report Comment Saved', '')


