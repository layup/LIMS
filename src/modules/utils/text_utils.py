import re

from base_logger import logger

def processClientInfo(jobNum, fileLocation):
    logger.info(f'Entering processClientInfo with jobNum: {jobNum}')

    clientInfoDict = {
        'clientName': '',
        'date': '',
        'time': '',
        'attn': '',
        'addy1': '',
        'addy2': '',
        'addy3': '',
        'sampleType1': '',
        'sampleType2': '',
        'totalSamples': '',
        'recvTemp': '',
        'tel': '',
        'email': '',
        'fax': '',
        'payment': ''
    }

    sampleNames = {}
    sampleTests = {}

    pageSize = 65;
    testsSection = 37;
    totalPageCounter = 0;

    if(fileLocation == None):
        logger.info('Completed Processing Client Info returning info')
        logger.info(f'Client Information Dictionary: {clientInfoDict}')
        logger.info(f'Sample Names: {repr(sampleNames)}')
        logger.info(f'Sample Tests: {sampleTests}')

        return clientInfoDict, sampleNames, sampleTests;

    with open(fileLocation) as file:
        logger.debug(f'Opening File: {repr(fileLocation)}')

        currentSampleName = '';
        sampleJob = ''

        for lineNumber, line in enumerate(file, 0):

            logger.debug(f'{lineNumber}: {repr(line)}')

            if(lineNumber < 10):
                process_client_info_text(lineNumber, line, clientInfoDict)

            if(lineNumber > 0 and lineNumber % 65 == 0):
                totalPageCounter+=1;

            # Section where we scan for sample names and sample tests
            if((lineNumber > (testsSection + (totalPageCounter * pageSize))) and line != '\n'):

                tests_check = re.search('(?<=\s-\s).*', line);
                sample_name_check = re.search(r'(?<=\s)(\d{1,2})(.*)', line)

                if(sample_name_check):
                    sampleNum = sample_name_check.group(1)
                    sampleName = sample_name_check.group(2).strip()
                    currentSampleName = sampleName
                    sampleJob = str(jobNum) + '-' + str(sampleNum)

                    logger.debug(f'Sample: {sampleJob}, Sample Name: {sampleName}')
                    sampleNames[sampleJob] = sampleName

                if(tests_check):
                    if(sampleJob in sampleTests):
                        sampleTests[sampleJob] = sampleTests[sampleJob] + ', ' + tests_check.group()
                    else:
                        sampleTests[sampleJob] = tests_check.group()

                if(sample_name_check == None and tests_check == None):
                    first_part = currentSampleName[:21].rstrip()
                    other_part = currentSampleName[21:]

                    sampleName = first_part + " " + line.strip() + " " + other_part;

                    sampleNames[sampleJob] = sampleName
    file.close()

    #process type sampleTests
    for key,value in sampleTests.items():
        testLists = [x.strip() for x in value.split(',')]
        sampleTests[key] = testLists

    logger.info('Exiting processClientInfo and returning')
    logger.info(f'Client Information Dictionary: ')

    for key, value in clientInfoDict.items():
        logger.info(f'*{key}: {repr(value)}')

    logger.info('Sample Information')
    logger.info(f'*sampleNames: {repr(sampleNames)}')
    logger.info(f'*sampleTests: {sampleTests}')

    return clientInfoDict, sampleNames, sampleTests;


def process_client_info_text(lineNumber, line, clientInfoDict):
    if(lineNumber == 1):
        clientInfoDict['clientName'] = line[0:54].strip()
        clientInfoDict['date'] = line[50:(54+7)].strip()
        clientInfoDict['time'] = line[65:71].strip()

    if lineNumber == 2:
        clientInfoDict['sampleType1'] = line[54:].strip()

        if "*" in line:
            clientInfoDict['attn'] = line[:54].strip()

        else:
            clientInfoDict['addy1'] = line[:54].strip()

    if(lineNumber == 3):
        clientInfoDict['sampleType2'] = line[54:].strip()

        if(clientInfoDict['attn'] != ''):
            clientInfoDict['addy1'] = line[:60].strip()
        else:
            clientInfoDict['addy2'] = line[:60].strip()

    if(lineNumber == 4):
        clientInfoDict['totalSamples'] = line[60:].strip()

        if(clientInfoDict['attn'] != ''):
            clientInfoDict['addy2'] = line[:60].strip()
        else:
            clientInfoDict['addy3'] = line[:60].strip()

    if(lineNumber == 5):
        if(clientInfoDict['attn'] and clientInfoDict['addy2']):
            clientInfoDict['addy3'] = line[:60].strip()
        else:
            clientInfoDict['tel'] = line[26:50].strip()

            try:
                clientInfoDict['recvTemp'] = line[71:].strip()
            except:
                logger.debug('No recv temp available')

    if(lineNumber == 6):
        clientInfoDict['tel'] = line[26:50].strip()
        clientInfoDict['recvTemp'] = line[71:].strip()

    if(lineNumber == 7):
        clientInfoDict['fax'] = line[26:].strip()

    if(lineNumber == 8):

        try:
            foundEmail = re.search('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', line).group()
            if(foundEmail):
                clientInfoDict['email'] = foundEmail;
        except:
            logger.error('Email Error')

        if("pd" in line.lower()):
            clientInfoDict['payment'] = line[51:].strip()