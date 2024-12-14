import os
from base_logger import logger

from modules.constants import elementSymbols
from modules.utils.excel_utils import *
from modules.utils.pickle_utils import load_pickle


def icp_create_excel(clientInfo, sampleNames, authorsInfo, jobNum,  sampleData, testInfo, unitType, limitElements, limits, footerComment):


    #TODO: missing the report type that will get called into this thing
    #TODO: determine how far out the longest thing is
    #FIXME: check out for none issue when they appear
    #TODO: tests how many of the tests need footer comments
    #TODO: determine how long the extra tests comments are
    #TODO: factor that into the size insertion

    logger.info('Entering icp_create_excel with parameters: ')
    logger.info(f'*jobNum        : {repr(jobNum)}')
    logger.info(f'*clientInfo    : {clientInfo}')
    logger.info(f'*authorsInfo   : {repr(authorsInfo)}')
    logger.info(f'*footerComment : {repr(footerComment)}')
    logger.info(f'*sampleNames   : {sampleNames}')
    logger.info(f'*sampleData    : {sampleData}')
    logger.info(f'*testInfo      : {testInfo}') #duplicate can remove?
    logger.info(f'*unitType      : {unitType}')
    logger.info(f'*limits        : {limits}')
    logger.info(f'*limitElements : {limitElements}')

    temp = load_pickle('data.pickle')
    exportPath = temp['reportsPath']

    newList = [item.lower() for item in testInfo]

    limitRef = {}

    for i, item in enumerate(limitElements):
        try:
            index = newList.index(item)
            limitRef[index] = limits[i]
        except:
            logger.error("could not find")

    logger.info(f'newList: {newList}')
    logger.info(f'limitRef: {limitRef}')

    wb = Workbook()
    ws = wb.active

    pageSetup(ws)

    reportTitle = 'ICP REPORT'
    createFooters(ws, reportTitle, jobNum)

    ws = insertClientInfo(ws, clientInfo, 'D')

    ws.column_dimensions['A'].width = 20 #120px
    ws.column_dimensions['H'].width = 19
    ws.print_title_rows = '1:8' # the first two rows

    #TODO: clean this up or deal with the sample names from the previous function
    temp = sampleData.keys()
    common_items = {key: value for key, value in sampleNames.items() if key in temp}

    sampleSections, samplePlacement = generateSampleHeaderNames(ws, common_items)

    totalTests = len(testInfo)
    totalPages = len(samplePlacement)

    totalCols = 8
    pageSize = 61

    pageLocation = 9
    usedSamples = 0

    #FIXME: include the length of the comments
    totalSamples = len(sampleData.keys())

    logger.info(f'Total Samples: {totalSamples}');
    formatRows(ws, totalSamples, totalCols, pageSize)

    for currentPage in range(totalPages):
        sampleAmount = len(samplePlacement[currentPage])
        logger.info(f'SampleAmount: {sampleAmount}');

        #first page information
        if(currentPage == 0):
            pageLocation = 9
            pageLocation = insertSampleName(ws, pageLocation, sampleSections[currentPage], totalCols)
            pageLocation = insertTestTitles(ws, pageLocation, sampleAmount, usedSamples, 1, totalCols )
            pageLocation = insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement[currentPage], sampleData, limitRef)

            if(totalPages > 1):
                insertNextPageComment(ws, pageLocation)
            else:
                insertIcpDocumentEnd(ws, pageLocation, footerComment, authorsInfo)

        else:
            pageLocation = (61 * currentPage) - (8 * (currentPage-1)) + 1
            logger.info(f'Starting Location: {pageLocation}')

            pageLocation = insertSampleName(ws, pageLocation, sampleSections[currentPage], totalCols)
            pageLocation = insertTestTitles(ws, pageLocation, sampleAmount, usedSamples, 1, totalCols)
            pageLocation = insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement[currentPage], sampleData, limitRef)

            if((currentPage+1) == totalPages):
                insertIcpDocumentEnd(ws, pageLocation, footerComment, authorsInfo)

            else:
                insertNextPageComment(ws, pageLocation)

        usedSamples += sampleAmount;

    maxWidth = ws.max_column
    logger.debug(f'The width of the worksheet is {repr(maxWidth)} columns')
    logger.debug(f'Ending Page location is: {pageLocation}');

    fileName = 'W' + str(jobNum) + ".001"
    filePath = os.path.join(exportPath, fileName)

    logger.info(f'Excel Report Created: {repr(fileName)}')
    logger.info(f'Exporting excel report to: {repr(filePath)}')

    wb.save(filePath)

    return filePath, fileName

#******************************************************************
#   Icp Excel Helper Functions
#******************************************************************

def insertIcpDocumentEnd(ws, pageLocation, footerComment, authorsInfo):
    logger.info(f'Entering insertIcpComment')

    pageLocation = insertComment(ws, pageLocation, footerComment)
    pageLocation +=2;

    if(len(authorsInfo) > 1):
        # two authors selected
        insertSignature(ws,pageLocation, [3,6], authorsInfo)
    else:
        # one author selected
        insertSignature(ws,pageLocation, [6], authorsInfo)


def insertIcpTests(ws, pageLocation, totalTests, testInfo, unitType, samplePlacement, sampleData, limitRef):
    logger.info('Entering insertIcpTests')
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

        logger.debug(f'{currentCol}: {currentCol}' )
        logger.debug(f'*Sample: {sample}, Column: {currentCol}')

        for j in range(0, totalTests+2):
            currentSample = ws.cell(row=counter+j, column=currentCol)
            currentSample.alignment = Alignment(horizontal='center', vertical='center')
            currentSample.border = Border(right=thinBorder)

            currentUnit = ws.cell(row=counter+j, column=7);

            comment = ws.cell(row=counter+j, column=8)
            comment.alignment = Alignment(horizontal='left', vertical='center', indent=1)

            currentVal = sampleData[sample][j]
            logger.debug(f'{j}: {currentVal}' )

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

    pageLocation = insertAdditionalTestsColumns(ws, pageLocation)

    # add bottom border
    for i in range(1,9):
        bottomBorder = ws.cell(row=pageLocation, column=i)
        bottomBorder.border = Border(top=thinBorder)

    pageLocation +=1;

    return pageLocation;

def insertAdditionalTestsColumns(ws, pageLocation):

    additionalTestsColumns = [1,2,7,8]


    # insert tests side comment section
    for current in additionalTestsColumns:

        temp = ws.cell(row=pageLocation, column=current)

        if(current != 8):
            temp.border = Border(right=thinBorder)
        else:
            #TODO: add different comments based m the hardness
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

    return pageLocation