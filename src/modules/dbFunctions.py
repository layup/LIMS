import sqlite3 

from base_logger import logger


def isValidDatabase(database_path):
    try:
        conn = sqlite3.connect(database_path)
        conn.close()
        return True
    except sqlite3.DatabaseError:
        print
        return False

#******************************************************************
#    CHM  Queries/Commands
#****************************************************************** 

def getAllChmTestsInfo(db): 
    try: 
        query = 'SELECT * FROM chemTestsInfo'    
        tests = db.query(query)    
        return tests 

    except Exception as e: 
        print(f'An error occurred: {e}')
        return None 

def getAllChmTestsInfo2(db): 
    try: 
        query = 'SELECT * FROM chemTestsInfo WHERE testName NOT LIKE "%ICP%"'    
        tests = db.query(query)    
        return tests 

    except Exception as e: 
        print(f'An error occurred: {e}')
        return None 

def getAllChmTestsInfo3(db): 
    try: 
        query = 'SELECT * FROM Tests WHERE testName NOT LIKE "%ICP%" ORDER BY testNum'    
        tests = db.query(query)    
        return tests 

    except Exception as e: 
        print(f'An error occurred: {e}')
        return None 
        

def addChmTestData(db, sampleNum, testNum, testValue, standardValue, unitValue, jobNum): 
    try: 
        query = 'INSERT INTO chemTestsData (sampleNum, testNum, testValue, standardValue, unitValue, jobNum) VALUES (?, ?, ?, ?, ?, ?)'
        db.execute(query, (sampleNum, testNum, testValue, standardValue, unitValue, jobNum, ))
        db.commit()

    except sqlite3.IntegrityError as e:
        print(e) 
    except Exception as e: 
        print(e)

        
def getChmTestData(db, sampleNum, testNum): 
    try: 
        query = 'SELECT * FROM chemTestsData WHERE sampleNum = ? and testNum = ?'
        result = db.query(query, (sampleNum, testNum))
        return result 
    
    except Exception as e: 
        print(e)
        return None 

def getAllChmTestsData(db):
    try: 
        query = 'SELECT jobNum, sampleNum, testNum, testValue, standardValue, unitValue FROM chemTestsData'
        results = db.query(query)
        return results

    except Exception as e: 
        print(e)

        
def getTestsName(db, testNum): 
    try: 
        query = 'SELECT testName FROM Tests WHERE testNum = ?'
        result = db.query(query, (testNum, ))
        return result 
        
    except Exception as e: 
        print(e)
        return None;

def getTestsTextName(db, testNum): 
    try: 
        query = 'SELECT benchChemName FROM Tests WHERE testNum = ?'
        result = db.query(query, (testNum, ))
        return result[0][0] 
        
    except Exception as e: 
        print(e)
        return None; 

def getTestsInfo(db, textName): 
    try: 
        #query = 'SELECT testNum, testName, benchMicroname, displayName, recoveryValue, recoveryValue FROM Tests WHERE benchMicroName = ?'
        query = 'SELECT * FROM chemTestsInfo WHERE textName = ?'
        result = db.query(query, (textName, ))
        return result[0]
        
    except Exception as e: 
        print(e)
        return None; 

#******************************************************************
#   ICP Queries/Commands 
#****************************************************************** 

#TODO: deal with it on the report side of things
def getIcpElements(db): 
    try: 
        query = 'SELECT * FROM icpElements'
        results = db.query(query)
        return results
        
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None

def getIcpElementsList(db):  
    try: 
        query = 'SELECT * FROM icpElements ORDER BY elementName ASC'
        results = db.query(query)
        return results
    except Exception as error: 
        print(f'[ERROR]: {error}')
        return None


def getIcpElementInfo(db, elementNum): 
    try: 
        query = 'SELECT * FROM icpElements WHERE elementNum = ? '
        results = db.query(query, (elementNum,))
        return results
        
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None

def getIcpElementLimits(db, elementNum): 
    try: 
        # Selecting all of the limits associated with that elementNum
        query = 'SELECT * FROM icpLimits WHERE elementNum = ?'  
        results = db.query(query, (elementNum,))
        return results
        
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None
    

def getIcpElements2(db): 

    try: 
        query = 'SELECT * FROM icpElements ORDER BY elementName ASC'
        definedElements = db.query(query)    
        return definedElements 
        
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None 
    
def getIcpLimitResults(database, parameters):
    try: 
        query = 'SELECT elementNum, unitType, lowerLimit, upperLimit, sideComment FROM icpLimits WHERE parameterNum = ?'
        result = database.query(query, (parameters, ))
        return {item[0]: [item[1], item[2], item[3], item[4]] for item in result}
        
    except Exception as e: 
        print(e)  
        return None 
    
def getIcpMachineData(database, jobNumber): 
    try: 
        query = 'SELECT sampleName, jobNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'
    
        return list(database.query(query, (jobNumber, )))

    except Exception as e: 
        print(e)  
        return None 

def addIcpElement(db): 
    pass; 
        

def updateIcpElement(db): 
    pass; 


def deleteIcpElement(db): 
    pass; 


def getReportNum(db, reportName): 
    try: 
        query = 'Select parameterNum FROM parameters WHERE parameterName = ?'
        parameterName = db.query(query, (reportName,))
        if(parameterName): 
            return parameterName[0][0]
        
    
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None


def updateIcpLimits(db, reportNum, elementNum, data ): 
    try: 
        unitType = data[0]
        lowerLimit = data[1]
        upperLimit = data[2]
        sideComment = data[3]
        
        query = 'INSERT OR REPLACE INTO icpLimits (parameterNum, elementNum, unitType, lowerLimit, upperLimit, sideComment) VALUES (?, ?, ? , ?, ?, ?)'
        db.execute(query, (reportNum, elementNum, unitType, lowerLimit, upperLimit, sideComment, ))
        db.commit()
    except Exception as e: 
        print(e)

        
def getIcpFooterComment(db, reportNum, elementNum): 
    try: 
        pass; 
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None; 



#******************************************************************
#    ICP Reports  
#****************************************************************** 

def addIcpReportFooter(db, parameterNum, footerComment): 
    try: 
        query = 'INSERT OR REPLACE INTO icpReports (parameterNum, footerComment) VALUES (?, ?)'
        db.execute(query, (parameterNum, footerComment,  ))
        db.commit()
   
    except Exception as e: 
        print(f'[ERROR]: {e}')

def getIcpReportFooter(db, parameterNum):
    try: 
        query = 'SELECT footerComment FROM icpReports WHERE parameterNum = ?'
        result = db.query(query, (parameterNum, ))
        return result[0][0] 
    
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None; 

#******************************************************************
#    CHEM Reports  
#****************************************************************** 
def addChmReportFooter(db, parameterNum, footerComment): 
    try: 
        query = 'INSERT OR REPLACE INTO chemReports (parameterNum, footerComment) VALUES (?, ?)'
        db.execute(query, (parameterNum, footerComment,  ))
        db.commit()
   
    except Exception as e: 
        print(f'[ERROR]: {e}')

def getChmReportFooter(db, parameterNum):
    try: 
        query = 'SELECT footerComment FROM chemReports WHERE parameterNum = ?'
        result = db.query(query, (parameterNum, ))
        return result[0][0] 
    
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None; 

     
#******************************************************************
#   Author Commands  
#****************************************************************** 

def getAuthorInfo(db, authorName): 
        try: 
            authorInfoQuery = 'SELECT * FROM authors WHERE authorName = ?'  
            db.execute(authorInfoQuery, (authorName, )) 
            result = db.fetchone()
            return result 
        except Exception as e: 
            print(e) 
            return None 

#******************************************************************
#    Settings Options 
#****************************************************************** 

def getAllParameters(db): 
    try: 
        query = 'SELECT * FROM parameters'  
        results = list(db.query(query))
        return results
        
    except Exception as e: 
        print(e)
        return None 

def getParameterNum(db, parameterName): 
    try: 
        query = 'SELECT parameterNum FROM parameters WHERE parameterName = ?'
        result = db.query(query, (parameterName,))[0][0]
        return result
     
    except Exception as e: 
        print(e)
        return None; 

def getParameterName(db, paramNum): 
    logger.debug(f"getParameterName called with db={db} and paramNum={paramNum}")

    try: 
        query = 'SELECT parameterName FROM parameters WHERE parameterNum = ?'  
        result = db.query(query, (paramNum,))[0][0]
        return result
    except Exception as e: 
        print(e)
        return None 
    
def addParameter(db, parameterName):
    try:
        query = 'INSERT INTO parameters (parameterName) VALUES (?)'
        db.execute(query, (parameterName,))
        db.commit()
    except Exception as e:
        print(e)

def deleteParameter(db, parameterNumber):
    try:
        query = 'DELETE FROM parameters WHERE parameterNumber = ?'
        db.execute(query, (parameterNumber,))
        db.commit()
    except Exception as e:
        print(e)

def updateParameter(db, parameterNumber, parameterName):
    try:
        query = 'UPDATE parameters SET parameterName = ? WHERE parameterNumber = ?'
        db.execute(query, (parameterName, parameterNumber))
        db.commit()
    except Exception as e:
        print(e)


def getAllAuthors(db): 
    try: 
        query = 'SELECT * FROM authors'  
        results = list(db.query(query))
        return results
        
    except Exception as e: 
        print(e)
        return None 

def getAllAuthorNames(db): 
    try: 
        query = 'SELECT authorName FROM authors'  
        results = list(db.query(query))
        return results
        
    except Exception as e: 
        print(e)
        return None 
    

def addAuthor(db, authorName, authorPosition): 
    try: 
        #TODO: fix the naming of this, check if this is a real issue
        query = 'INSERT INTO authors (authorName, authorPostion) VALUES (?, ?)' 
        db.execute(query, (authorName, authorPosition))
        db.commit()
            
    except Exception as e: 
        print(e) 
    

def deleteAuthor(db, authorNum): 
    try: 
        query = 'DELETE FROM authors WHERE authorNum = ?' 
        db.execute(query, (authorNum, ))
        db.commit()
            
    except Exception as e: 
        print(e)  

def updateAuthor(db, authorNum, authorName, authorPosition):
    
    try: 
        query = 'UPDATE authors SET authorName = ? , authorRole = ? WHERE authorNum = ?'
        db.execute(query, (authorName, authorPosition, authorNum))
        db.commit()
    
    except Exception as e: 
        print(e)
     

    
#******************************************************************
#    Report Queries
#****************************************************************** 

def addNewJob(db, jobNum, reportNum, parameter, dilution, status, currentDate):
    try: 
        sql = 'INSERT INTO jobs (jobNum, reportNum, parameterNum, status, creationDate, dilution) values (?,?,?, ?,?,?)'
        db.execute(sql, (jobNum, reportNum, parameter, status, currentDate, dilution))
        db.commit()
    except Exception as e: 
        print(f'An error occurred: {e}')
        
def getAllJobsList(db): 
    try:
        query = 'SELECT * FROM jobs ORDER BY creationDate DESC'  
        results = list(db.query(query)) 
        return results
    except Exception as e:
        print(f"An error occurred during the database query: {e}")
        return None

def getAllJobNumbersList(db):  
    try: 
        query = 'SELECT DISTINCT jobNum FROM jobs'  
        db.execute(query)

        jobNumbers = db.fetchall()
        return  [item[0] for item in jobNumbers] 

    except Exception as e:
        print(f'An error occurred: {e}')
        return []

def getJobStatus(db, jobNum, reportNum): 
    try: 
        query = 'SELECT status FROM jobs WHERE jobNum = ? and reportNum = ?'
        result = db.query(query, (jobNum, reportNum)) 
        return result[0][0]
        
    except Exception as e: 
        print(f'An error occurred: {e}')
        return None 

def getReportTypeList(db): 
    query = 'SELECT * FROM icpReportType' 
    report_types = db.query(query)
    return [item[0] for item in report_types]

def updateJob(db, jobNum, reportNum, parameter, dilution, status, currentDate):
    try: 
       # sql = 'INSERT INTO jobs (jobNum, reportNum, parameterNum, status, creationDate, dilution) values (?,?,?, ?,?,?)'
        sql = 'UPDATE jobs SET status = ?, creationDate = ?, dilution = ? WHERE jobNum = ? AND reportNum = ? AND parameter = ?'
        db.execute(sql, (status, currentDate, dilution, jobNum, reportNum, parameter))
        db.commit()
    except Exception as e: 
        print(f'An error occurred: {e}') 

def updateJobStatus(db, jobNum, reportNum, status): 
    try: 
        query = 'UPDATE jobs SET status = ? WHERE jobNum = ? AND reportNum = ?' 
        db.execute(query, (status, jobNum, reportNum))
        db.commit()
        
        logger.info(f'Successfully updated {jobNum} status: {status}')
        
    except Exception as error: 
        print(error)
        print(f'Could not update {jobNum} status' )

def checkJobExists(db, jobNum, reportNum): 
    try: 
        query = 'SELECT * FROM jobs WHERE jobNum = ? and reportNum = ?'
        db.execute(query, (jobNum, reportNum))
        result = db.fetchone()
        return result
    except Exception as e: 
        print(f'An error occurred: {e}')
        return None     


def searchJobsList(db, searchValue): 
    try:
        query = 'SELECT * FROM jobs WHERE jobNum LIKE ? ORDER BY creationDate DESC'
        results = list(db.query(query, (searchValue + '%',)))
        return results
    except Exception as e:
        print(f"An error occurred during the database query: {e}")
        return None

#******************************************************************
#    Front Database Queries 
#****************************************************************** 

def getFrontHistory(db): 
    query = 'SELECT jobNumber, companyName, creationDate, status FROM history'  
    db.execute(query)

    jobNumbers = db.fetchall()
    return  [item[0] for item in jobNumbers]