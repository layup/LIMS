import os
from base_logger import logger

from modules.utils.excel_utils import *
from modules.utils.pickle_utils import load_pickle


def createChmReport(clientInfo, jobNum, authorsInfo, reportComment, sampleNames, sampleData, testInfo, unitType, recovery):
    logger.info(f'Entering CreateChmReport with parameters:')
    logger.info(f'*jobNum       : {repr(jobNum)}') 
    logger.info(f'*ClientInfo   : {repr(clientInfo)}') 
    logger.info(f'*authorsInfo  : {repr(authorsInfo)}')
    logger.info(f'*reportComment: {repr(reportComment)}')
    logger.info(f'*sampleNames  : {repr(sampleNames)}') 
    logger.info(f'*sampleData   : {repr(sampleData)}') 
    logger.info(f'*testInfo     : {repr(testInfo)}') 
    logger.info(f'*unitType     : {repr(unitType)}') 
    logger.info(f'*recovery     : {repr(recovery)}') 

   
    #FIXME: pickle saving and loading without being fucked up, get path of where things should be saved
    temp = load_pickle('data.pickle') 
    exportPath = temp['reportsPath']

    logger.info(f'Preparing to create excel document')
    
    wb = Workbook()
    ws = wb.active
    
    pageSetup(ws); 
    
    logger.info(f'Preparing to add footers to excel document:')
    reportTitle = 'CHM REPORT'
    createFooters(ws, reportTitle, jobNum); 

    #SETTING UP MAIN INFORMATION 
    #TODO: determine how far out the longest thing is 
    #FIXME: check out for none issue when they appear
    
    ws = insertClientInfo(ws, clientInfo, 'D')
    ws.column_dimensions['A'].width = 20 #120px 
    ws.column_dimensions['H'].width = 19
    ws.print_title_rows = '1:8' # the first two row
    
    totalCols = 8 
    pageSize = 61    
    #pageSize = 56; 
 
    totalSamples = len(sampleData.keys())
    logger.debug(f'Total Samples: {totalSamples}')
    
    #FIXME: so page amounts change based on column width, so takes in how many pages we want 
    formatRows(ws, totalSamples, totalCols, pageSize);
    
    logger.info('Preparing to generate sample header names ')
    sampleSections, samplePlacement = generateSampleHeaderNames(ws, sampleNames)
    
    allocatedSpace = 20; 
    
    testSize = len(testInfo)
    tableSize = 6 + testSize 
    
    totalSampleSections = len(sampleSections)
    totalTablesWithComments = math.floor((pageSize - allocatedSpace)/tableSize)
    totalPages = math.ceil(totalSampleSections/totalTablesWithComments)
   
    logger.debug('Calculating Excel Report Information') 
    logger.debug(f'Total Sample Sections: {totalSampleSections}')
    logger.debug(f'Tables with comments : {totalTablesWithComments}' )
    logger.debug(f'Total Pages          : {totalPages}')
    
    usedSamples = 0; 
    pageLocation = 9; 
    totalTests = len(testInfo)

    #determine when the next page is? 
    #TODO: can change it so the file names follow the naming convention of just go in order
    counter = 0; 
    
    logger.info('Preparing to write excel file')  
    for currentPage in range(totalPages): 
        logger.debug(f'Current Page: {currentPage} out of {totalPages}')
        sampleAmount = len(samplePlacement[counter])
  
        if(currentPage != 0): 
            pageLocation = (pageSize * currentPage) - (8 * (currentPage-1)) + 1  
        else: 
            pageLocation = 9; 
            
        logger.debug(f'Page Location: {pageLocation}')
        
        if(currentPage+1 == totalPages): 
            logger.debug("Last Page")
            remainingSamples = totalSampleSections - counter; 
            
            for i in range(remainingSamples): 
                pageLocation = insertSampleName(ws, pageLocation, sampleSections[counter], totalCols)
                pageLocation = insertTestTitles(ws,pageLocation, sampleAmount, usedSamples, 0, totalCols)
                pageLocation = insertTestInfo(ws,pageLocation, testInfo, samplePlacement[counter], sampleData, totalTests, unitType, recovery)
                
                if(i+1 == remainingSamples): 
                    pageLocation = insertComment(ws, pageLocation, reportComment)
                    pageLocation+=2; 
                    
                    if(len(authorsInfo) > 1): 
                        insertSignature(ws,pageLocation, [3,6], authorsInfo)
                    else:
                        insertSignature(ws,pageLocation, [6], authorsInfo) 

                counter+=1; 
                usedSamples += 4;
        
        #not the last page
        else: 
            logger.debug('Not last page')
            for i in range(totalTablesWithComments): 
                pageLocation = insertSampleName(ws, pageLocation, sampleSections[counter], totalCols)
                pageLocation = insertTestTitles(ws,pageLocation, sampleAmount, usedSamples, 0, totalCols)
                pageLocation = insertTestInfo(ws,pageLocation, testInfo, samplePlacement[counter], sampleData, totalTests, unitType, recovery)   
                
                if(i+1 == totalTablesWithComments): 
                    insertNextPageComment(ws, pageLocation)
                    
                counter+=1; 
                usedSamples += 4; 
       
    #set the width back to automatic 
    #ws.page_setup.fitToPage = False 
    
    fileName = 'W' + str(jobNum) + ".chm" 
    filePath = os.path.join(exportPath, fileName)

    logger.info(f'Excel Report Created: {repr(fileName)}')
    logger.info(f'Exporting excel report to: {repr(filePath)}')
    
    wb.save(filePath)

    return filePath, fileName

    
    