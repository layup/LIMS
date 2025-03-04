from PyQt5.QtGui import QIcon

#******************************************************************
#   Report Variables
#******************************************************************

ICP_REPORT = 1
CHM_REPORT = 2

REPORTS = {
    'ICP': 1,
    'CHM': 2,
    1: 'ICP',
    2: 'CHM'
}

REPORTS_TYPE = ['','CHM','ICP']
REPORT_NUM = {
    'ICP': 1,
    'CHM': 2
}
REPORT_NAME = {
    1: 'ICP',
    2: 'CHM'
}
REPORT_STATUS = {
    0: 'Not Generated',
    1: 'Generated'
}
MACHINE_TYPE = {
    1: 'Differential Optical Spectroscopy (DOS)',
    2: 'Mass Spectrometry (MOS)'
}


REPORT_FILTER = ['Date Created', 'Status', 'Parameter', 'Job Number', 'Report Type']
ICP_FILTER = ['Upload Date', 'Sample Number', 'Job Number']
CHM_FILTER = ['Upload Date, ']


#******************************************************************
#    UI Variables
#******************************************************************

SMALL_BTN = 12
MED_BTN = 13
BIG_BTN = 14

#******************************************************************
#    Table Variables
#******************************************************************

TABLE_ROW_HEIGHT    = 23
TABLE_COL_SMALL     = 90
TABLE_COL_MED       = 140
TABLE_COL_LARGE     = 240

SMALL_COL = 140
MED_COL = 240
LARGE_COL = 340


#******************************************************************
#    Tree Variables
#******************************************************************

TREE_ROW_HEIGHT     = 20

FILTER_BY = [
    'Sample Number',
    'JobNunmber',
    'Machine Type',
    'File Location',
    'Upload Date'
]

SHOW_ENTITIES = [
    '50',
    '75',
    '100',
    '150'
]


#******************************************************************
#    Global Icons
#******************************************************************

EDIT_ICON = QIcon('assets/icons/edit_icon.svg')
DELETE_ICON = QIcon('assets/icons/delete_button.svg')
#SAVE_ICON = QIcon('assets/icons/save.svg')




periodic_table1 = {
    'Ag': 'Silver',
    'Al': 'Aluminium',
    'Au': 'Gold',
    'B': 'Boron',
    'Ba': 'Barium',
    'Be': 'Beryllium',
    'Ca': 'Calcium',
    'Co': 'Cobalt',
    'Cr': 'Chromium',
    'Cu': 'Copper',
    'Fe': 'Iron',
    'K': 'Potassium',
    'La': 'Lanthanum',
    'Mg': 'Magnesium',
    'Mn': 'Manganese',
    'Mo': 'Molybdenum',
    'Na': 'Sodium',
    'Ni': 'Nickel',
    'P': 'Phosphorus',
    'S': 'Sulfur',
    'Sc': 'Scandium',
    'Si': 'Silicon',
    'Sn': 'Tin',
    'Sr': 'Strontium',
    'Ti': 'Titanium',
    'V': 'Vanadium',
    'W': 'Tungsten',
    'Zn': 'Zinc'
}

periodic_table_2 = {
    'As': 'Arsenic',
    'Se': 'Selenium',
    'Cd': 'Cadmium',
    'Sb': 'Antimony',
    'Hg': 'Mercury',
    'Pb': 'Lead',
    'U': 'Uranium'
}

#34
periodic_table = {
    'Ag': 'Silver',
    'Al': 'Aluminium',
    'Au': 'Gold',
    'As': 'Arsenic',
    'B': 'Boron',
    'Ba': 'Barium',
    'Be': 'Beryllium',
    'Ca': 'Calcium',
    'Cd': 'Cadmium',
    'Co': 'Cobalt',
    'Cr': 'Chromium',
    'Cu': 'Copper',
    'Fe': 'Iron',
    'Hg': 'Mercury',
    'K': 'Potassium',
    'La': 'Lanthanum',
    'Mg': 'Magnesium',
    'Mn': 'Manganese',
    'Mo': 'Molybdenum',
    'Na': 'Sodium',
    'Ni': 'Nickel',
    'P': 'Phosphorus',
    'Pb': 'Lead',
    'S': 'Sulfur',
    'Sb': 'Antimony',
    'Sc': 'Scandium',
    'Se': 'Selenium',
    'Si': 'Silicon',
    'Sn': 'Tin',
    'Sr': 'Strontium',
    'Ti': 'Titanium',
    'U': 'Uranium',
    'V': 'Vanadium',
    'W': 'Tungsten',
    'Zn': 'Zinc'
}

elementSymbols = {v: k for k, v in periodic_table.items()}
icpMachine2Symbols = ['As', 'Se', 'Cd', 'Hg', 'Pb', 'U']

icpReportRows = ['Ag', 'Al', 'Au', 'B', 'Ba', 'Be', 'Ca', 'Co', 'Cr', 'Cu', 'Fe', 'K', 'La', 'Mg', 'Mn', 'Mo', 'Na', 'Ni', 'P', 'S', 'Sc', 'Si', 'Sn', 'Sr', 'Ti', 'V', 'W', 'Zn', 'As', 'Se', 'Cd', 'Sb', 'Hg', 'Pb', 'U']


###Excel Constants

