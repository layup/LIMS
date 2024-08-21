

#******************************************************************
#   Report Variables
#******************************************************************

ICP_REPORT = 1 
CHM_REPORT = 2 

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

#******************************************************************
#    Table Variables
#******************************************************************

TABLE_ROW_HEIGHT    = 20 
TREE_ROW_HEIGHT     = 20 


SAMPLETYPES = [ 
    '1um wound fiter', 
    'sediment',
    'agar plates', 
    'clams', 
    'compost', 
    'drinking water', 
    'effluent', 
    'filters(s)', 
    'fish', 
    'food', 
    'ore',
    'other', 
    'paint', 
    'saltwater', 
    'soil',
    'swab',
    'water',
]

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



GSMS_values = {
    "001": ["ALkalinity", "mg/L"], 
    "002": ["NH3-N", "ug/L "], 
    "003": ["Cl-", 'mg/L'], 
    "004": ['E.C', 'us/cm'], 
    "005": ['F-', 'mg/L'], 
    "006": ['TKN', 'mg/L'], 
    "007": ['Mn', 'mg/L'], 
    "008": ['NO3-N', 'ug/L'], 
    "009": ['NO2-N', 'ug/L'], 
    "010": ['ortho-PO43', 'ug/L'],
    "011": ['pH', ' '], 
    "012": ['TPO43 --P', 'ug/L'], 
    "013": ['D.TO43 --P', 'ug/L'], 
    "014": ['SO42', 'mg/L'], 
    "015": ['T.O.C', 'mg/L'], 
    "016": ['T&L', 'mg/L'],
    "017": ['TDS', 'mg/L'], 
    "018": ['TSS', 'mg/L'],
    "019": ['Turbidity', 'NTU'], 
    "020": ['UVT', '%'] 
}

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

