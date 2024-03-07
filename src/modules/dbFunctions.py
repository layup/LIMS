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
#    General  Queries/Commands
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
