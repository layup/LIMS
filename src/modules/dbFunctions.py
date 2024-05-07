import sqlite3 

from widgets.widgets import * 

#******************************************************************
#    CHM  Queries/Commands
#****************************************************************** 

def getChmTotalTests(db): 
    query = 'SELECT count(*) FROM gcmsTests'
    
    db.execute(query)
    total = db.fetchone()[0]
    
    return total; 

def deleteChmData(db, sampleNum, testsName): 
    try: 
        query = 'DELETE FROM gcmsTestsData WHERE sampleNum = ? and testsName = ?'
        db.execute(query, [sampleNum, testsName])
        db.commit()
    except Exception as e: 
        print(f'Error, could not delete item {sampleNum}: {testsName}')
        print(e)
        return None; 

def loadChmTotalTest(db): 
    query = 'SELECT * FROM gcmsTests'
    return db.query(query)

def loadChmTestsData(db): 
    query = 'SELECT * FROM gcmsTestsData ORDER BY jobNum ASC'
    results = db.query(query, [])
    return results 

def insertChmTests(db, txtName, unitType, recoveryVal, displayName): 
    try:
        definedTestsValues = 'INSERT OR REPLACE INTO gcmsTests (testName, unitType, recoveryVal, displayName) VALUES (?,?,?, ?)' 
        db.execute(definedTestsValues, (txtName, unitType, recoveryVal, displayName) )
        db.commit()

    except sqlite3.IntegrityError as e:
        print(e)
    except Exception as e: 
        print(e)


#******************************************************************
#    ICP Queries/Commands 
#****************************************************************** 
#TODO: rename all of the load items to get items? 

def getIcpElements(db): 
    query = 'SELECT * FROM icpElements ORDER BY element ASC'
    definedElements = db.query(query)    
    return definedElements   

def getIcpFooterComment(db, reportType): 
    pass; 

def getIcpElementsList(db): 
    query = 'SELECT element, symbol FROM icpElements ORDER BY element ASC' 
    
    elements = list(db.query(query))
    
    return elements

def getTotalElements(db): 
    amountQuery = 'SELECT count(*) FROM icpElements'
    
    db.execute(amountQuery)
    total = db.fetchone()[0]
    
    return total; 

#TODO: define which report this is going to be  
def getElementLimits(db): 
    elementsQuery = 'SELECT element FROM icpLimits WHERE reportType = ? ORDER BY element ASC'
    elementWithLimits = db.query(elementsQuery, ('Water',))    

    temp = []

    for item in elementWithLimits: 
        #print(item)
        temp.append(item[0]) 

    return temp; 

# Gets all of the machine data and process the data
def getMachineData(db, jobNum): 
    pass; 


def loadIcpMachineHistory(db, offset, limit=50):
    # offset is the starting section that I will, so offset 50 will be 51 forward 
    query = 'SELECT * FROM icpMachineData1 ORDER BY createdDate DESC LIMIT ? OFFSET ?'
    
    db.execute(query, (limit, offset))
    result = db.fetchone()
    return result
    

def loadIcpElement(db, elementName): 
    query = 'SELECT * FROM icpElements WHERE element = ?'
    db.execute(query, (elementName,))
    result = db.fetchone() 

    return result
    
def loadIcpLimit(db, elementName, reportType): 
    query = 'SELECT * FROM icpLimits WHERE element = ? and ReportType = ?'
    db.execute(query, (elementName, reportType))
    result =  db.fetchone() ;
    return result 

def loadIcpReportList(db): 
    try: 
        query = 'SELECT * FROM icpReportType' 
        results = db.query(query)
        
        return results
    except Exception as e: 
        print(f'An error occured: {e}')
        return None 
    
def loadIcpFooterComment(db, reportType):  
    query = 'SELECT footerComment from icpReportType WHERE reportType = ?'
    db.execute(query, (reportType,))
    result = db.fetchone()
    return result

#******************************************************************
#    NEW ICP Database Connections 
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


def getIcpElementNum(db, elementName): 
    pass; 


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

        

def getIcpFooterComment(db, reportNum, elementNum): 
    try: 
        pass; 
    except Exception as e: 
        print(f'[ERROR]: {e}')
        return None; 



#******************************************************************
#    General Queries/Commands
#****************************************************************** 

def checkReportExists(db, jobNum, reportType): 
    try: 
        query = 'SELECT * FROM jobs WHERE jobNum = ? and reportType = ?'
        db.execute(query, (jobNum, reportType))
        result = db.fetchone()
        return result
    except Exception as e: 
        print(f'An error occured: {e}')
        return None 

def searchJobsList(db, searchValue): 
    try:
        query = 'SELECT * FROM jobs WHERE jobNum LIKE ? ORDER BY creationDate DESC'
        results = list(db.query(query, (searchValue + '%',)))
        return results
    except Exception as e:
        print(f"An error occurred during the database query: {e}")
        return None

def getAllJobsList(db): 
    try:
        query = 'SELECT * FROM jobs ORDER BY creationDate DESC'  
        results = list(db.query(query)) 
        return results
    except Exception as e:
        print(f"An error occurred during the database query: {e}")
        return None
   
def getAllJobNumbersList(db):  
    query = 'SELECT DISTINCT jobNum FROM jobs'  
    db.execute(query)

    jobNumbers = db.fetchall()
    return  [item[0] for item in jobNumbers]

def getReportTypeList(db): 
    query = 'SELECT * FROM icpReportType' 
    report_types = db.query(query)
    return [item[0] for item in report_types]
     
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
#TODO: import previous functions later on 



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
    

def addAuthor(db, authorName, authorPostion): 
    try: 
        query = 'INSERT INTO authors (authorName, authorPostion) VALUES (?, ?)' 
        db.execute(query, (authorName, authorPostion))
        db.ecommit()
            
    except Exception as e: 
        print(e) 
    

def deleteAuthor(db, authorNum): 
    try: 
        query = 'DELETE FROM authors WHERE authorNum = ?' 
        db.execute(query, (authorNum, ))
        db.ecommit()
            
    except Exception as e: 
        print(e)  

def updateAuthor(db, authorNum, authorName, authorPostion):
    
    try: 
        query = 'UPDATE authors SET authorName = ? , authorRole = ? WHERE authorNum = ?'
        db.execute(query, (authorName, authorPostion, authorNum))
        db.commit()
    
    except Exception as e: 
        print(e)
     
    


#******************************************************************
#    Client Queries
#****************************************************************** 




#******************************************************************
#    Front Database Queries 
#****************************************************************** 

def getFrontHistory(db): 
    query = 'SELECT jobNumber, companyNamme, creationDate, status FROM history'  
    db.execute(query)

    jobNumbers = db.fetchall()
    return  [item[0] for item in jobNumbers]