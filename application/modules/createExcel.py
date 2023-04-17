
import os 

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, borders, Border, Side
from openpyxl.cell.rich_text import TextBlock, CellRichText
from openpyxl.worksheet.page import PageMargins

from openpyxl.worksheet.header_footer import HeaderFooter

import math 
import re 


from modules.utilities import * 


pageRows = 46
defaultFont = Font(name="Times New Roman")

#Borders 
thinBorder = Side(border_style="thin", color="000000")
doubleBorder = Side(border_style='double', color="000000")


def createIcpReport(): 
    
    pass 


def createGcmsReport(clientInfo, sampleNames, sampleData, testInfo, unitType):
    
    print(clientInfo)
    print(sampleNames)
    print(sampleData)
    print(testInfo)
    print(unitType)
   
    
    #FIXME: picke saving and loading without being fucked up 
    #get the pickle path of 
    temp = load_pickle('data.pickle')
    writePath = temp['ispDataUploadPath']
    
    
    #create a new workbook and select the active worksheet 
    wb = Workbook()
    ws = wb.active
    
   # set the default view to page layout
    ws.sheet_view.view = "pageLayout" 

    # Set the page width to auto
    page_setup = ws.page_setup
    
    #page_setup.fitToPage = True
    page_setup.fitToWidth = 1
  
    font = Font(name='Times New Roman')
    ws.sheet_format.font = font; 

    createFooters(ws); 

    #SETTING UP MAIN INFORMATION 
    #TODO: determine how far out the longest thing is 
    #FIXME: check out for none issue when they appear
    

    ws = createHeader(ws, clientInfo, 'D')
    ws.column_dimensions['A'].width = 20 #120px 
    ws.print_title_rows = '1:8' # the first two rows
    
    #determine how many rows the sample name will take 

    sampleSections = []
    samplePlacement = []
    currentWord = ''
    temp = []
    
    
    #determine how many sample sections we will need 
    
    #can only display 4 at a time 
    for i, (key,value) in enumerate(sampleNames.items(), start=1): 
        
        stripedWord = " ".join(value.split())

        #print(key," ".join(value.split()))
        currentWord += " " + str(i) + ") " + stripedWord + " "
        temp.append(key)

        if(i % 4 == 0): 
            print(currentWord)
            sampleSections.append(currentWord)
            samplePlacement.append(temp)
            currentWord = ""
            temp = []
        
    #insert sample names section
    insertSampleName(ws, 9, sampleSections[0])
    
    #TODO: Determine how much of spacing and what not we need 
    pageLocation = 12; 
    
    totalSamples = len(sampleData)
    totalTests = len(testInfo)
    totalRows = 8 
    
    #TODO:  add new column for comments 
    pageLocation = insertTestTitles(ws, pageLocation, totalSamples, 0)

    #INSERT TEST INFORMATION 
    pageLocation = insertTestInfo(ws, pageLocation, testInfo, samplePlacement[0], sampleData, totalTests, unitType)
    
    
    #INSERT THE REMAINING PAGES 
    currentPage = 0; 
    

    if(len(sampleSections) > 1): 
        for i, currentSample in enumerate(sampleSections): 
            print(i, currentSample)
            if(i != 0): 
            
                testRowAmount = 2 + 1 + totalTests + 1 
                #not last one 
                if(i + 1 != len(sampleSections)):
                    
                    #test total + current placement + add endspace 
                    temp = testRowAmount + pageLocation + 2 
                    if(nextPage(temp,currentPage)):
                        
                        insertSampleName(ws, pageLocation, currentSample)
                        pageLocation+=2;
                        
                        pass; 
                    else: 
                        currentPage+=1; 
                    
                #last row 
                else: 
                    #TODO: include comments and signautres 
                    temp = testRowAmount + pageLocation + 2 
                    if(nextPage(temp,currentPage)):
                        
                        insertSampleName(ws, pageLocation, currentSample)
                        pageLocation+=2;
                        pageLocation+=1; 
                        pageLocation = insertTestTitles(ws,pageLocation, totalTests, i * 4)
                        pageLocation = insertTestInfo(ws,pageLocation, testInfo, samplePlacement[i], sampleData, totalTests, unitType)
                        pageLocation = insertComments(ws,pageLocation)
                        
                    else: 
                        #next page 
                        currentPage+=1; 
                        
                    pass; 
                    
    
    font = Font(name="Times New Roman")

    # Apply the font to all cells in the worksheet
    for row in ws.iter_rows():
        for cell in row:
            cell.font = font


    cell = ws['A50']
    ''' 
    cell.value = CellRichText([
        TextBlock(text='normal text', font=Font(bold=False)),
        TextBlock(text='bold text', font=Font(bold=True)),
    ])
    '''
    
    wb.save('example.xlsx')
    

def createIcpReport(clientInfo, sampleNames, sampleData, testInfo, unitType, limitElements, limits): 
    print(clientInfo)
    print(sampleNames)
    print(sampleData)
    print(testInfo)
    print(unitType)
    print(limitElements)
    print(limits)

    newList = [item.lower() for item in testInfo]
    
    print(newList)
    limitRef = {}
    
    for i, item in enumerate(limitElements): 
        try: 
            index = newList.index(item)
            limitRef[index] = limits[i]
        except:
            print("could not find") 
            
        
    print(limitRef)

    
    

    wb = Workbook()
    ws = wb.active
    
   # set the default view to page layout
    ws.sheet_view.view = "pageLayout" 

    # Set the page width to auto
    page_setup = ws.page_setup
    
    #setup page size 
    page_setup.fitToPage = True
    page_setup.fitToHeight = False 
    page_setup.fitToWidth = True
    #page margins 
    
    page_margins = PageMargins()
    page_margins.left = 0.7
    page_margins.right = 0.7
    page_margins.top = 0.75
    page_margins.bottom = 0.75
    page_margins.header = 0.3
    page_margins.footer = 0.3
    
    ws.page_margins = page_margins
    
  
    font = Font(name='Times New Roman')
    ws.sheet_format.font = font; 

    createFooters(ws); 

    #SETTING UP MAIN INFORMATION 
    #TODO: determine how far out the longest thing is 
    #FIXME: check out for none issue when they appear
    #TODO: add the job number to the end of this thing mf 
        
    ws = createHeader(ws, clientInfo, 'D')
    ws.column_dimensions['A'].width = 20 #120px 
    ws.print_title_rows = '1:8' # the first two rows
    
    #determine how many rows the sample name will take 
    sampleSections = []
    samplePlacement = []    
    selectedNames = []
    
    currentWord = ''
    temp = []
    
    #determine how many sample sections we will need 
    for key in sampleData: 
        selectedNames.append(key)
        

    #can only display 4 at a time 
    print('!------ GENERATING SAMPLE NAME ------!')
    for i, sampleNum in enumerate(selectedNames, start=1): 
        sampleName = sampleNames[sampleNum]
        condencedName = " ".join(sampleName.split())
        currentWord += " " + str(i) + ") " + condencedName + " "
        temp.append(sampleNum)

        if(i % 4 == 0): 
            sampleSections.append(currentWord)
            samplePlacement.append(temp)
            currentWord = ""
            temp = []
        
    if(len(temp) != 0): 
        sampleSections.append(currentWord)
        samplePlacement.append(temp)
        currentWord = ""
        temp = [] 
            

    #insert sample names section
    insertSampleName(ws, 9, sampleSections[0])
    
    #TODO: Determine how much of spacing and what not we need 
    pageLocation = 12; 
    
    totalSamples = len(sampleData)
    totalTests = len(testInfo)
    totalRows = 8 
   
    pageLocation = insertTestTitles(ws, pageLocation, totalSamples, 0) 
    #for row in range(len(testInfo)): 
    
    #46 * 15 = 690  
        
    unitCol = 7
        
    counter = pageLocation; 
    for item in range(len(testInfo)): 
        elementRow = ws.cell(row=counter, column=1); 
        symbolRow = ws.cell(row=counter, column=2); 
        unitRow = ws.cell(row=counter, column=unitCol)
        
        
        elementRow.value = "{0}) {1}".format(item+1, testInfo[item])

        temp = testInfo[item]
        symbolRow.value = elementSymbols[temp]
        #print(item)
        try: 
            unitRow.value = unitType[item]
        except: 
            print("error")
        
        elementRow.border = Border(right=thinBorder) 
        symbolRow.border  = Border(right=thinBorder) 
        unitRow.border    = Border(right=thinBorder) 
        
        symbolRow.alignment = Alignment(horizontal='center', vertical='center')
        unitRow.alignment   = Alignment(horizontal='center', vertical='center')
        
        ws.row_dimensions[counter].height = 13
        
        
        
        
        counter+=1; 
   
    counter = pageLocation 
    sampleLocation = 0 

    for i, sample in enumerate(samplePlacement[0], start=3): 
        
        print(i, sample)
        
        for j in range(0, len(testInfo)): 
            currentSample = ws.cell(row=counter+j, column=i)        
            currentSample.alignment = Alignment(horizontal='center', vertical='center')  
            currentSample.border = Border(right=thinBorder)
            
            currentVal = sampleData[sample][j]
            #print(currentVal)
            #print(j)
            
            #FIXME: this is wrong atm uncal means something else 
            try: 
                temp = float(currentVal)
                
                if j in limitRef: 
                    print(j)
                    lower = limitRef[j][1]
                    higher = limitRef[j][2]
                    
                    currentSample.value = temp 
                    
                    if(lower != ''): 
                        if(temp < lower): 
                            print('lower')
                            currentSample.value = '< ' + str(lower)

                            
                    if(higher != ''): 
                        if(temp > higher): 
                            print('higher')
                            currentSample.value = '> ' + str(higher)

                    
                else: 
                    currentSample.value = temp 
                    
                
            except:
                if(currentVal == 'Uncal'):
                    currentSample.value = 'n/a'
                else: 
                    currentSample.value = currentVal
                    
            #print(currentSample.value)
            
        


    sampleLocation += 1 
    pageLocation += totalTests;  
    
    print(pageLocation)
    
    maxWidth = ws.max_column 
    print(f'The width of the worksheet is {maxWidth} columns')


        
    font = Font(name="Times New Roman", size=9)

    # Apply the font to all cells in the worksheet
    for row in ws.iter_rows():
        
        for cell in row:
            cell.font = font 
            
            if(cell.row < 10): 
                ws.row_dimensions[cell.row].height = 13

          
            

    
    wb.save('example2.xlsx')


def createFooters(ws): 
    
    #Setting up the headers and footers 
    ws.oddHeader.fontName = 'Times New Roman'
    ws.oddHeader.fontSize = 14

    ws.evenHeader.left.font_name = 'Times New Roman'
    ws.evenHeader.left.font_size = 14
    
    ws.oddHeader.left.text  = 'GCMS - Report Form: &D'
    ws.evenHeader.left.text = 'GCMS - Report Form: &D' 
    
    
    ws.oddHeader.right.text  = "Page &P of &N"
    ws.evenFooter.right.text = "Page &P of &N"
    
    ws.oddFooter.left.text  = '&BT:&B 250 656 1334 \n&BE:&B info@mblabs.com'
    ws.evenFooter.left.text = '&BT:&B 250 656 1334 \n&BE:&B info@mblabs.com' 
    
    ws.oddFooter.center.text = "&B MB Laboratories Ltd.&B \nwww.mblabs.com "
    ws.evenFooter.center.text= "&B MB Laboratories Ltd.&B \nwww.mblabs.com "
    
    ws.oddFooter.right.text = '&BMail:&B PO BOX 2103 Stn Main \n Sidney, B.C, V8L 356'
    ws.evenFooter.right.text ='&BMail:&B PO BOX 2103 Stn Main \n Sidney, B.C, V8L 356'
    

def createHeader(ws, clientInfo, column2): 
    
    ws['A1'] = clientInfo['clientName']
    
    #font = Font(size=9)
    #ws['A1'].font = font
    
    if(clientInfo['attn'] is None): 
        ws['A2'] = '*' 
    else: 
        ws['A2'] = clientInfo['attn'] 
        
    ws['A3'] = clientInfo['addy1']
    ws['A4'] = clientInfo['addy2'] + ", " + clientInfo['addy3']
    
    ws['A6'] = 'TEL' + clientInfo['tel']
    ws['A7'] =  clientInfo['email']
    
    ws[column2 + '1'] = "Date: " + clientInfo['date'] + "  (" + clientInfo['time'] + ")" 
    ws[column2 + '2'] = "Source: " + clientInfo['sampleType1']
    ws[column2 + '3'] = "Type: " + clientInfo['sampleType2']
    ws[column2 + '4'] = "No. of Samples: " + clientInfo['totalSamples']
    ws[column2 + '5'] = "Arrival temp: " + clientInfo['recvTemp']
    ws[column2 + '6'] = "PD: " + clientInfo['payment']
    
    return ws 
     
def createComments(ws):
    pass;      

def mergeSampleSection(ws, row, col): 
    
    pass; 

def nextPage(curVal, curPage): 
    
    #minue 9 for each interation that we increase 
    
    pageEnds = [47]
    
    for i in range(10):
        pageEnds.append(pageEnds[i] + 37)
        
    
    if(curVal > pageEnds[curPage]): 
        print('FALSE')
        return False 
    else: 
        print("TRUE")
        return True; 

def insertSampleName(ws, row, sampleSection): 
    
    temp = ws.cell(row=row, column=1)
    temp.value = 'Samples: ' + sampleSection
    temp.border = Border(bottom=thinBorder)
   
    ws.merge_cells(start_row=row, start_column=1, end_row=row+1, end_column=8)
    temp.alignment = Alignment(wrap_text=True) 
    
def insertTestTitles(ws, pageLocation, totalSamples, startVal ): 
    tests = ws.cell(row=pageLocation, column=1)
    tests.value = 'Tests'

    units = ws.cell(row=pageLocation, column=2)
    units.value = 'Units'
    units.border = Border(right=thinBorder, left=thinBorder)
    units.alignment = Alignment(horizontal='center', vertical='center')

    if(totalSamples >= 4): 
        for i in range(4): 
           sample = ws.cell(row=pageLocation, column=i+3)
           sample.value = 'Sample ' + str(startVal + i +1) 
           sample.alignment = Alignment(horizontal='center', vertical='center')
           sample.border = Border(right=thinBorder, left=thinBorder) 
              
           
    else: 
        for i in range(totalSamples): 
            sample = ws.cell(row=pageLocation, column=i)
            sample.value = 'Sample ' + str(startVal + i + 1) 
            sample.alignment = Alignment(horizontal='center', vertical='center')
            sample.border = Border(right=thinBorder, left=thinBorder) 
            
    so = ws.cell(row=pageLocation, column=7) 
    so.value = 'So'
    so.border = Border(right=thinBorder, left=thinBorder)
    so.alignment = Alignment(horizontal='center', vertical='center') 
    
    ref = ws.cell(row=pageLocation, column=8)
    ref.value = 'Ref Value'  
    ref.alignment = Alignment(horizontal='center', vertical='center')  
    
    pageLocation+=1; 
    
    for i in range(1,9): 
        current = ws.cell(row=pageLocation, column=i) 
      
        if(i != 1): 
            current.alignment = Alignment(horizontal='center', vertical='center')
        
        if(i == 9):
           current.border = Border(bottom=thinBorder) 
        else: 
            current.border = Border(right=thinBorder, bottom=doubleBorder)
    

    pageLocation+=1; 

    return pageLocation 

def insertTestInfo(ws, pageLocation, testInfo, samplePlacement, sampleData, totalTests, unitType): 

    counter = pageLocation
    ''' 
    for test in testInfo: 
        test = re.sub('[^A-Za-z0-9]+', '', test)
        testPlacement = ws.cell(row=counter, column=1)
        testPlacement.value = test 
        testPlacement.border = Border(right=thinBorder)
        counter+=1
    '''
    

    for item in range(len(testInfo)): 
        currentTest = re.sub('[^A-Za-z0-9]+', '', testInfo[item])
        testPlacement = ws.cell(row=counter, column=1)
        unitPlacement = ws.cell(row=counter, column=2)
        
        testPlacement.value = currentTest
        unitPlacement.value = unitType[item]
        
        testPlacement.border = Border(right=thinBorder) 
        unitPlacement.alignment = Alignment(horizontal='center', vertical='center')
        
        counter+=1; 
    
    
    
    counter = pageLocation 
    sampleLocation = 0 
    for i, sample in enumerate(samplePlacement, start=3): 
        
        currentResults = sampleData[sample]
        
        for j in range(0,totalTests): 
            currentSample = ws.cell(row=counter+j,column=i)
            currentSample.alignment = Alignment(horizontal='center', vertical='center')
            
            if(type(currentResults[j]) == (int or float)): 
               
                currentSample.value = float(currentResults[j])
            else:
                currentSample.value = currentResults[j]
            
            currentSample.value = currentResults[j]
            currentSample.border = Border(right=thinBorder, left=thinBorder)
            
            
    sampleLocation += 1 
    pageLocation += totalTests-1; 
    
    for i in range(1,9): 
        ws.cell(row=pageLocation, column=i).border = Border(bottom=thinBorder)
        
        if(i == 9):
            ws.cell(row=pageLocation, column=i).border = Border(bottom=thinBorder)
    
    pageLocation += 2; 
    nameLocation = 1; 
    
    return pageLocation; 

def insertComments(ws, pageLocation): 

    comments = { 
        "SD":  'SD    = standard devition;       REF VALUE = primary or secondary reference material', 
        'STD': 'STD  = secondary standard calibrated to primary standard reference material', 
        'So':  'So     = standard deviation at zero analyte concentration; method detection limit is generally', 
        'So2': '       considered to be 3x So value', 
        'ND':  'ND   = none is detcted;          n/a = not applicable'
    }
    
    for i, (key,value) in enumerate(comments.items()): 
        temp = ws.cell(row = pageLocation+i, column=1)
        temp.value = value
        
    pageLocation+=6; 
    return pageLocation; 



    
    
    



def insertSignature(ws, pageLocation): 
    
    name1 = 'R. Bilodeau'
    title1 = 'Analytical Chemist'
    name2 = 'H. Hartmann'
    

def insertTestTitlesIcp():
    pass;  

def insertTestInfoIcp(): 
    pass; 