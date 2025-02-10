import re;

from datetime import date
from base_logger import logger

from PyQt5.QtGui import QIntValidator, QDoubleValidator

from modules.constants import REPORTS_TYPE, REPORT_NUM, REPORT_STATUS
from modules.dialogs.basic_dialogs import okay_dialog, error_dialog, yes_no_cancel_dialog
from modules.dialogs.create_report_dialog import CreateReport
from modules.utils.text_utils import processClientInfo
from modules.utils.file_utils import scanForTXTFolders

from pages.reports_page.reports.report_utils import clearDataTable, populate_author_dropdown, clearLayout
#from pages.reports_page.reports.create_icp_report import icpReportLoader
from pages.reports_page.chm.chm_report_setup import chm_report_setup
from pages.reports_page.icp.icp_report_setup import icp_report_setup


###################################################################
#    creating new or opening  jobs
####################################################################

#TODO: see if I can have a client info that contains it all
def general_reports_setup(self):
    logger.info('Entering general_reports_setup')

    self.create_report = CreateReport(self.parameters_manager)
    self.create_report.process_data.connect(lambda data: handle_create_new_job(self, data))

def handle_create_new_job(self, data):
    logger.info(f'Entering handle_create_new_job with data: {data}')

    jobNum, report_id, param_id, dilution = data

    dilution = 1 if (dilution == '' or dilution is None) else dilution

    # scan for file path in the folder
    text_file_path = scanForTXTFolders(jobNum)

    # Error checking section
    error_checks = validate_report_inputs(jobNum, report_id, param_id, text_file_path)

    if(sum(error_checks) == 0):
        logger.info('Error Checks Passed')

        self.create_report.close()

        currentDate = date.today()
        currentStatus = 0

        self.jobNum = jobNum
        self.report_id = report_id
        self.parameter = param_id
        self.dilution = dilution

        job_exists_check = self.jobs_manager.check_job_exist(self.jobNum, self.report_id)

        # process the .txt file and get the necessary information
        # TODO: need to have these in self since i've build so much of the excel on that
        self.clientInfo, self.sampleNames, self.sampleTests = processClientInfo(jobNum, text_file_path)

        if(job_exists_check is None):
            logger.info('Job does not exist')

            # create new job entry into the database
            self.jobs_manager.add_job(jobNum, self.report_id, param_id, dilution, currentStatus)

        else:
            logger.info('Job does exist')

            title = f'Report {jobNum} Already Exists'
            message = 'Would you like to load existing report or overwrite report?'
            overwrite_status = yes_no_cancel_dialog(title, message)

            if(not overwrite_status):
                return

            #TODO: maybe watch for what No does
            if(overwrite_status == 'Cancel' or overwrite_status == 'No'):
                return

            # update the job entry database section
            self.jobs_manager.update_job(jobNum, self.report_id, param_id, dilution, currentStatus)

            # load in the status of not generated
            self.ui.statusHeaderLabel.setText(REPORT_STATUS[currentStatus])

        try:
            # Prepare the layout based on if it is ICP or CHM Report
            prepare_report_layout_config(self, self.report_id, text_file_path)

        except Exception as error:
            logger.error(error)
            error_dialog('Error Creating Report', f'Could not create report {self.jobNum}')
            print(error)
            return

        # Switch the index of items
        self.ui.reportsTab.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(5)

    else:
        report_error_handler(error_checks)


#TODO: have them get passed correctly
def open_existing_job(self, existing_data):
    logger.info('Entering open_existing_job')

    jobNum = str(existing_data.jobNum)
    report_id = existing_data.report
    parameter = existing_data.parameter
    dilution = existing_data.dilution

    print(f'report_id: {report_id}')

    text_file_location = scanForTXTFolders(jobNum)

    # Error checking section
    #TODO: rename the errors for this one
    error_checks = validate_report_inputs(jobNum, report_id, parameter, text_file_location)
    logger.debug(f'error_checks: {error_checks}')

    if(sum(error_checks) == 0):

        #TODO: move away from having global functions like this
        self.jobNum = jobNum
        self.report_id = report_id
        self.parameter = parameter
        self.dilution = dilution

        job_exists_check = self.jobs_manager.check_job_exist(self.jobNum, self.report_id)

        if(job_exists_check):

            # load in the client information
            #TODO: load it from the database instead
            self.clientInfo, self.sampleNames, self.sampleTests = processClientInfo(self.jobNum, text_file_location)

            # set the header information
            job_status = self.jobs_manager.get_status(self.jobNum, self.report_id)

            try:
                self.ui.statusHeaderLabel.setText(REPORT_STATUS[job_status])
            except Exception as error:
                logger.error(error)
                self.ui.statusHeaderLabel.setText(job_status)

            # Prepare to load the data for either CHM or ICP report
            prepare_report_layout_config(self, self.report_id, text_file_location)

            # Switch the index of items
            self.ui.reportsTab.setCurrentIndex(0)
            self.ui.stackedWidget.setCurrentIndex(5)

        else:
            error_dialog('Error Loading Report', f'Could not load the report {self.jobNum}')
            return

    else:
        report_error_handler(error_checks)

###################################################################
#    Error Handling
####################################################################

def prepare_report_layout_config(self, reportNum, filePath):
    self.logger.info(f'Entering prepare_layout_config with parameter: reportType: {repr(reportNum)}')

    # Load the client information
    load_client_info(self)

    # Load in the text tab
    load_client_text_file(self, filePath)

    # Populate drop down authors
    populate_author_dropdown(self)

    # clear the layout, clear the table, clear the widget samples
    clearDataTable(self.ui.dataTable)

    clearLayout(self.ui.samplesContainerLayout_2)

    #TODO: could move all of the btns into their own thing
    if(reportNum == 1):
        logger.info('Preparing ICP report Configuration')

        #self.ui.reloadDataBtn.setVisible(True)
        self.ui.calcHardnessBtn.setVisible(True)

        self.ui.createIcpReportBtn.setVisible(True)
        self.ui.createChmReportBtn.setVisible(False)
        self.ui.icpDataField.show()

        #TODO: clean this up a bit better
        sampleTests, sampleNames = process_icp_tests_names(self)

        #icpReportLoader(self)
        icp_report_setup(self, sampleTests, sampleNames)

    if(reportNum == 2):
        logger.info('Preparing CHM report Configuration')

        #self.ui.reloadDataBtn.setVisible(False)
        self.ui.calcHardnessBtn.setVisible(False)

        self.ui.createIcpReportBtn.setVisible(False)
        self.ui.createChmReportBtn.setVisible(True)
        self.ui.icpDataField.hide()

        # load in all the necessary information before switching pages
        chm_report_setup(self)

    # reload the lab page just in case
    self.chem_history_controller.update_view()

def process_icp_tests_names(self):
    logger.info('Entering process_icp_tests_names')

    approved = {}

    element_symbols = self.elements_manager.get_element_symbols()

    for sample_name, tests in self.sampleTests.items():
        icp_tests = []

        for test in tests:
            # Check if item has icp or contained within element_symbols
            if('icp' in test.lower() or test.lower() in element_symbols):
                icp_tests.append(test)

        if(len(icp_tests) > 0):
            approved[sample_name] = icp_tests
            logger.info(f'{sample_name}, {icp_tests}')

    new_names_list = {key: self.sampleNames[key] for key in self.sampleNames if key in approved}

    for key, value in new_names_list.items():
        logger.info(f'{key}, {value}')

    return approved, new_names_list

###################################################################
#    Error Handling
####################################################################

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

###################################################################
#    Helper Functions
####################################################################

def load_client_text_file(self, filePath):
    logger.info('Entering load_client_text_file')

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

#TODO: add me to this
def load_report_header_info(self, jobNum, clientName, parameter, reportType, dilution, status=None):
    # Set the header parameters
    self.ui.jobNum.setText(f"W{str(jobNum)}")
    self.ui.clientNameHeader.setText(clientName)
    self.ui.parameterHeader.setText(str(parameter))
    self.ui.reportTypeHeader.setText(str(reportType))
    self.ui.factorHeader.setText(str(dilution))

    if(status):
        self.ui.statusHeaderLabel.setText(status)
    else:
        self.ui.statusHeaderLabel.setText('N/A')

def load_client_info(self, client_info=None):
    logger.info("Entering load_client_info")

    parm_item = self.parameters_manager.get_param_info(self.parameter)

    report_names = {1: 'ICP', 2: 'CHM'}  # Store report names in a dictionary
    report_name = report_names.get(self.report_id, 'N/A')
    self.ui.reportTypeHeader.setText(report_name)

    parameter_name = parm_item.param_name if parm_item else 'N/A'
    self.ui.parameterHeader.setText(parameter_name)

    # Set the header parameters
    self.ui.jobNum.setText(f"W{str(self.jobNum)}")
    self.ui.clientNameHeader.setText(self.clientInfo.get('clientName', ''))
    self.ui.factorHeader.setText(str(self.dilution))

    # Define a mapping of UI elements to client info fields
    field_mapping = {
        self.ui.clientName_1: "clientName",
        self.ui.date_1: "date",
        self.ui.time_1: "time",
        self.ui.attention_1: "attn",
        self.ui.addy1_1: "addy1",
        self.ui.addy2_1: "addy2",
        self.ui.addy3_1: "addy3",
        self.ui.sampleType1_1: "sampleType1",
        self.ui.sampleType2_1: "sampleType2",
        self.ui.totalSamples_1: "totalSamples",
        self.ui.recvTemp_1: "recvTemp",
        self.ui.tel_1: "tel",
        self.ui.email_1: "email",
        self.ui.fax_1: "fax",
        self.ui.payment_1: "payment",
    }

    # Populate client info fields
    for widget, field in field_mapping.items():
        widget.setText(self.clientInfo.get(field, ""))

    logger.info("Populated Client")
