import re;

from datetime import date
from base_logger import logger

from modules.dialogs.basic_dialogs import error_dialog, yes_no_cancel_dialog
from modules.dialogs.create_report_dialog import CreateReport
from modules.utils.text_utils import process_txt_client_info
from modules.utils.file_utils import scan_for_txt_folders

from modules.utils.report_utils import clear_data_table, populate_author_dropdown, clear_layout
from pages.reports_page.chm.chm_report_setup import chm_report_setup
from pages.reports_page.icp.icp_report_setup import icp_report_setup

from modules.models.report_item import ReportItem

def general_reports_setup(self):
    logger.info('Entering general_reports_setup')

    self.create_report = CreateReport(self.parameters_manager)
    self.create_report.process_data.connect(lambda data: handle_create_new_report(self, data))

def handle_create_new_report(self, data):
    logger.info(f'Entering handle_create_new_report with data: {data}')

    jobNum, report_id, param_id, dilution = data
    dilution = 1 if (dilution == '' or dilution is None) else dilution

    text_file_path = scan_for_txt_folders(jobNum)
    error_checks = validate_report_inputs(jobNum, report_id, param_id, text_file_path)

    if(sum(error_checks) == 0):
        # close the create_report dialog
        self.create_report.close()

        check_report_exists = self.reports_manager.get_report(jobNum, report_id)

        if(check_report_exists is None):
            # report doesn't exists, add report to database
            self.reports_manager.add_report(jobNum, report_id, param_id , dilution)
        else:
            current_status = 0

            overwrite_status = yes_no_cancel_dialog(
                title=f'Report {jobNum} Already Exists',
                message='Would you like to load existing report or overwrite report?'
            )

            if(not overwrite_status):
                return

            # report does exist and have selected to overwrite existing data
            self.reports_manager.update_report(jobNum, report_id, param_id, dilution)
            self.reports_manager.update_status(jobNum, report_id, current_status)

        try:
            prepare_report_layout_config(self, jobNum, report_id, param_id, dilution, current_status, text_file_path)
        except Exception as error:
            error_dialog('Error Creating Report', f'Could not create report {jobNum}')
            logger.error(error)
            return
    else:
        report_error_handler(error_checks)
        logger.debug(f'error_checks: {error_checks}')

def open_existing_report(self, existing_data):
    logger.info('Entering open_existing_report')

    jobNum = str(existing_data.jobNum)
    report_id = existing_data.report
    param_id = existing_data.parameter
    dilution = existing_data.dilution

    text_file_path = scan_for_txt_folders(jobNum)
    error_checks = validate_report_inputs(jobNum, report_id, param_id, text_file_path)

    if(sum(error_checks) == 0):
        check_report_exists = self.reports_manager.get_report(jobNum, report_id)

        if(check_report_exists):
            report_status = self.reports_manager.get_report_status(jobNum, report_id) # Should return either a 0 or 1
            #TODO: get the selected authors

            prepare_report_layout_config(self, jobNum, report_id, param_id, dilution, report_status, text_file_path)

        else:
            error_dialog('Error Loading Report', f'Could not load the report {jobNum}')
            return
    else:
        report_error_handler(error_checks)
        logger.debug(f'error_checks: {error_checks}')

def prepare_report_layout_config(self, job_num, report_id, param_id, dilution, status, text_file_path):
    self.logger.info(f'Entering prepare_layout_config with job_num: {job_num}, report_id: {report_id}, param_id: {param_id}, dilution: {dilution}, status: {status}, text_file_path: {text_file_path}')

    client_info , sample_names, sample_tests = process_txt_client_info(job_num, text_file_path)

    # create active report item
    self.active_report = ReportItem(self.client_manager, self.reports_manager, job_num, report_id, param_id, dilution)
    self.active_report.process_sample_names(sample_names)
    self.active_report.process_sample_tests(sample_tests)

    # load the client information on the report page
    self.active_report.process_client_info(client_info)

    client_name = self.client_manager.get_client_info('clientName')

    load_report_header_info(self, job_num, report_id, param_id, dilution, status, client_name)
    load_text_file_tab(self, text_file_path)
    populate_author_dropdown(self)

    # clear the tests data table & sample layout of the widget sample items
    clear_data_table(self.ui.dataTable)
    clear_layout(self.ui.samplesContainerLayout_2)

    if(report_id == 1):
        configure_icp_report(self, sample_names, sample_tests)
    elif(report_id == 2):
        configure_chm_report(self, sample_names, sample_tests)

    self.ui.reportsTab.setCurrentIndex(0)
    self.ui.stackedWidget.setCurrentIndex(5)

    # reload the lab page just in case
    # self.chem_history_controller.update_view()

def configure_icp_report(self, sample_names, sample_tests):
    logger.info('Preparing ICP report Configuration')

    self.ui.calcHardnessBtn.setVisible(True)
    self.ui.createIcpReportBtn.setVisible(True)
    self.ui.createChmReportBtn.setVisible(False)
    self.ui.icpDataField.show()

    icp_report_setup(self, sample_names, sample_tests)

def configure_chm_report(self, sample_names, sample_tests):
    logger.info('Preparing CHM report Configuration')

    self.ui.calcHardnessBtn.setVisible(False)
    self.ui.createIcpReportBtn.setVisible(False)
    self.ui.createChmReportBtn.setVisible(True)
    self.ui.icpDataField.hide()

    chm_report_setup(self, sample_names, sample_tests)


def validate_report_inputs(jobNum, reportType, parameter, textFileExists):
    logger.info('Entering validate_report_inputs')
    logger.debug(f'jobNum: {jobNum}, reportType: {reportType}, parameter: {parameter}, textFileExists: {textFileExists}')

    report_types = ['','CHM','ICP', 1, 2]

    return [
        0 if re.match('^([0-9]{6})$', jobNum) else 1,
        0 if reportType in report_types else 1,
        0 if (parameter != '' and parameter) else 1,
        0 if textFileExists != '' and textFileExists else 1,
    ]

def report_error_handler(error_checks):
    logger.info('report_error_handler called with parameters: error_checks {error_checks}')

    errorTitle = 'Cannot Proceed to Report Creation Screen'
    errorMsg = ''

    if(error_checks[0] == 1):
        print('Error: Please Enter a valid job number')
        errorMsg += 'Please Enter a Valid Job Number\n'

    if(error_checks[1] == 1):
        print("Error: Please Select a reportType")
        errorMsg += 'Please Select a Report Type\n'

    if(error_checks[2] == 1):
        print('Error: Please Select a parameter')
        errorMsg += 'Please Select a Parameter\n'

    if(error_checks[3] == 1):
        print("Error: TXT File doesn't exist")
        errorMsg += 'TXT File could not be located\n'

    error_dialog(errorTitle, errorMsg)

def load_text_file_tab(self, filePath):
    logger.info('Entering load_text_file_tab')

    # Enable Text File Tab if the file is there
    if(filePath):
        try:
            self.ui.reportsTab.setTabEnabled(2, True)

            with open(filePath) as file:
                content = file.read()

            # Clear existing content in the QTextBrowser
            self.ui.textBrowser.clear()

            # Append the content of the text file to the QTextBrowser
            self.ui.textBrowser.append(content)

        except Exception as error:
            print(error)
            self.ui.reportsTab.setTabEnabled(2, False)

    else:
         self.ui.reportsTab.setTabEnabled(2, False)

def load_report_header_info(self, job_num:int, report_id:int, param_id:int, dilution, status, client_name:str):
    logger.info('Entering load_report_header_info')

    # set the basic header info
    self.ui.jobNum.setText(f"W{str(job_num)}")
    self.ui.clientNameHeader.setText(client_name)
    self.ui.factorHeader.setText(str(dilution))

    # set report name
    report_names = {1: 'ICP', 2: 'CHM'}  # Store report names in a dictionary
    report_name = report_names.get(report_id, 'N/A')
    self.ui.reportTypeHeader.setText(report_name)

    # set parameter name
    parm_item = self.parameters_manager.get_param_info(param_id)
    parameter_name = parm_item.param_name if parm_item else 'N/A'
    self.ui.parameterHeader.setText(parameter_name)

    # set status
    status_opts = {0: "Not Generated", 1: "Generated"}
    status_opt = status_opts.get(status, 'N/A')
    self.ui.statusHeaderLabel.setText(status_opt)
