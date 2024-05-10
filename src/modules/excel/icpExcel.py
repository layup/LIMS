from modules.utilities import * 
from modules.constants import *
from modules.createExcel import *


def createIcpReport(clientInfo, sampleNames, jobNum,  sampleData, testInfo, unitType, limitElements, limits, footerComment): 
    
    #TODO: missing the report type that will get called into this thing 
    #TODO: determine how far out the longest thing is 
    #FIXME: check out for none issue when they appear
    #TODO: tests how many of the tests need footer comments 
    #TODO: determine how long the extra tests comments are 
    #TODO: factor that into the size insertion 

    print('ICP general Information')
    print(clientInfo)
    print(sampleNames)
    print(sampleData)
    print(testInfo)
    print(unitType)
    print(limitElements)
    print(limits)
    print('-------------------------')
        
    temp = load_pickle('data.pickle') 
    exportPath = temp['reportsPath']

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
    
    pageSetup(ws);    
    reportTitle = 'ICP REPORT'
    createFooters(ws, reportTitle, jobNum); 

    ws = createHeader(ws, clientInfo, 'D')
    ws.column_dimensions['A'].width = 20 #120px 
    ws.column_dimensions['H'].width = 19 
    ws.print_title_rows = '1:8' # the first two rows
    
    #determine how many rows the sample name will take 
    sampleSections = []
    samplePlacement = []    
    selectedNames = []
        
    #determine how many sample sections we will need 
   
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
            
    print('Sample Placement: ', samplePlacement)
    print('Sample Sections: ', sampleSections)
    
    totalTests = len(testInfo)
    totalPages = len(samplePlacement)
    
    totalCols = 8 
    pageSize = 61; 
    pageLocation = 9; 
    usedSamples = 0; 
    
    #FIXME: include the length of the comments 
    totalSamples = len(sampleData.keys())
    
    print('Total Samples: ', totalSamples);
    formatRows(ws, totalSamples, totalCols, pageSize)

    for currentPage in range(totalPages): 
        
        sampleAmount = len(samplePlacement[currentPage])
        print('Sample Amount: ', sampleAmount);
        
        #first page infomation 
        if(currentPage == 0): 
            pageLocation = 9; 
            pageLocation = insertSampleName(ws, pageLocation, sampleSections[currentPage], totalCols)
            pageLocation = insertTestTitles(ws, pageLocation, sampleAmount, usedSamples, 1, totalCols ) 
            pageLocation = insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement[currentPage], sampleData, limitRef) 
            
            if(totalPages > 1): 
                comment = ws.cell(row=pageLocation, column=1)
                comment.value = 'Continued on next page ....'
                comment.font = Font(bold=True, size=9, name="Times New Roman")
            else: 
                insertIcpComment(ws, footerComment, pageLocation)
                  
        else: 
            pageLocation = (61 * currentPage) - (8 * (currentPage-1)) + 1 
            print('Starting Location: ', pageLocation) 
            pageLocation = insertSampleName(ws, pageLocation, sampleSections[currentPage], totalCols)
            pageLocation = insertTestTitles(ws, pageLocation, sampleAmount, usedSamples, 1, totalCols) 
            pageLocation = insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement[currentPage], sampleData, limitRef) 
            
            if((currentPage+1) == totalPages): 
                insertIcpComment(ws, footerComment, pageLocation)
                
            else: 
                comment = ws.cell(row=pageLocation, column=1)
                comment.value = 'Continued on next page ....'
                comment.font = Font(bold=True, size=9, name="Times New Roman")
        
        usedSamples += sampleAmount; 
    
    maxWidth = ws.max_column 
    print(f'The width of the worksheet is {maxWidth} columns')
    print('Current Page location: ', pageLocation); 
    
    fileName = 'W' + str(jobNum) + ".001" 
    filePath = os.path.join(exportPath, fileName)
    print('Export Path: ', filePath)

    # Create the directory if it doesn't exist
    #if not os.path.exists(exportPath):
    #    os.makedirs(exportPath)
 
    wb.save(filePath)
    


def insertIcpComment(ws, footerComment, pageLocation): 
    for (i, value) in enumerate(footerComment):
        comment = ws.cell(row=pageLocation, column=1)
        comment.value = value
        comment.font = Font(size=9, name="Times New Roman") 
        pageLocation+=1; 
    '''     
    additonalComments = [
        'Comments:', 
        'All constituents tested meet Canadian and B.C drinking water standards.'
    ]

    for currentComment in additonalComments: 
        comment = ws.cell(row=pageLocation, column=1)
        comment.value = currentComment 
        pageLocation+=1; 
    '''
    pageLocation +=2; 
    insertSignature(ws, pageLocation, [3,6])


def insertComments(ws, pageLocation): 

    comments = { 
        "SD":  'SD    = standard devition;       Standard Recovery = primary or secondary reference material', 
        'STD': 'STD  = secondary standard calibrated to primary standard reference material', 
        'ND':  'ND   = none is detcted;          n/a = not applicable'
    }
    
    for i, (key,value) in enumerate(comments.items()): 
        temp = ws.cell(row = pageLocation+i, column=1)
        temp.value = value
        
    pageLocation+=5; 
    
    return pageLocation; 


def insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement, sampleData, limitRef): 
    counter = pageLocation; 
    
    #FIXME: need to change because will be loading elements and symbols based on the info 
    for item in range(totalTests): 
        elementRow = ws.cell(row=counter, column=1); 
        symbolRow = ws.cell(row=counter, column=2); 
        unitRow = ws.cell(row=counter, column=7)
        
        elementRow.value = "{0}) {1}".format(item+1, testInfo[item].capitalize())

        temp = testInfo[item]
        symbolRow.value = elementSymbols[temp.capitalize()]
        
        elementRow.border = Border(right=thinBorder) 
        symbolRow.border  = Border(right=thinBorder) 
        unitRow.border    = Border(right=thinBorder, left=thinBorder) 
        
        symbolRow.alignment = Alignment(horizontal='center', vertical='center')
        unitRow.alignment   = Alignment(horizontal='center', vertical='center')
        
        counter+=1; 
   
    counter = pageLocation 
    sampleLocation = 0 

    #inserts the sample values, unitType, limits and comments 
    for currentCol, sample in enumerate(samplePlacement, start=3): 
        
        print(currentCol, sample)
        print(f'**Sample: {sample}, Column: {currentCol}')
        
        for j in range(0, totalTests+2): 
            currentSample = ws.cell(row=counter+j, column=currentCol)        
            currentSample.alignment = Alignment(horizontal='center', vertical='center')  
            currentSample.border = Border(right=thinBorder)
            
            currentUnit = ws.cell(row=counter+j, column=7); 
            
            comment = ws.cell(row=counter+j, column=8)
            comment.alignment = Alignment(horizontal='left', vertical='center', indent=1)   
            
            currentVal = sampleData[sample][j]
            print(j, currentVal)

            if(floatCheck(currentVal)): 
                currentVal = float(currentVal) 
                
                if j in limitRef: 
                    lowerLimit = limitRef[j][1]
                    upperLimit = limitRef[j][2]
                    
                    currentSample.value = significantFiguresConvert(currentVal)
                    
                    if lowerLimit and currentVal < lowerLimit:
                        currentSample.value = f'< {lowerLimit:.3f}' 
                        
                    #if(currentVal == 0): 
                    #    currentSample.value = f'< {lowerLimit:.3f}' 
                else: 
                    currentSample.value = significantFiguresConvert(currentVal)   
                    
                   #if(currentVal == 0): 
                    #     currentSample.value =  f'< {lowerLimit:.3f}' 
                        
            else: 
                currentSample.value = 'ND'

                if(currentVal == 'Uncal'): 
                    if j in limitRef:                 
                        lowerLimit = limitRef[j][1] 
                        if(lowerLimit): 
                            currentSample.value = f' < {lowerLimit:.3f}' 
                        
            if j in limitRef: 
                upperLimit = limitRef[j][2]
                limitComment = limitRef[j][3]
                unitType = limitRef[j][4]

                currentUnit.value = unitType

                if(limitComment): 
                    comment.value = limitComment
                #FIXME: insert the unit value if exists 
                elif(upperLimit): 
                    comment.value = f'{significantFiguresConvert(upperLimit)} {unitType}'

                else: 
                    comment.value = 'no limit listed'
            else: 
                comment.value = 'no limit listed' 
                
    sampleLocation += 1 
    pageLocation += totalTests;  

    additionalTestsColumns = [1,2,7,8]
    
    for current in additionalTestsColumns: 
        
        temp = ws.cell(row=pageLocation, column=current)
        
        if(current != 8): 
            temp.border = Border(right=thinBorder)
        else: 
            #TODO: add differet comments basedp m the hardness 
            temp.value = '0-75 mg/L = soft'
            temp.alignment = Alignment(horizontal='left', vertical='center', indent=1)   
        
        if(current == 1):
            temp.value = 'Hardness'
            
        if(current == 2): 
            temp.value = 'CaCO₃'
            temp.alignment = Alignment(horizontal='left', vertical='center', indent=1)   
            
        if(current == 7):
            temp.value = 'mg/L'
            temp.alignment = Alignment(horizontal='center', vertical='center') 
            temp.border = Border(right=thinBorder, left=thinBorder)
            
    pageLocation+=1; 

    for current in additionalTestsColumns: 
        temp = ws.cell(row=pageLocation, column=current)
       
        if(current != 8): 
            temp.border = Border(right=thinBorder)
        else: 
            temp.value = '7.0 to 10.5' 
            temp.alignment = Alignment(horizontal='left', vertical='center', indent=1)   
        
        if(current == 1):
            temp.value = 'Ph'
        
        if(current == 7):
            temp.value = 'units'
            temp.alignment = Alignment(horizontal='center', vertical='center') 
            temp.border = Border(right=thinBorder, left=thinBorder)
            
    pageLocation+=1; 
    
    for i in range(1,9): 
        bottomBorder = ws.cell(row=pageLocation, column=i)
        bottomBorder.border = Border(top=thinBorder)
            
    pageLocation +=1; 
    
    return pageLocation; 

