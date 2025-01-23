import sqlite3

from base_logger import logger



#******************************************************************
#    Table: Tests
#******************************************************************

def getAllChmTestsInfo3(db):
    try:
        query = 'SELECT * FROM Tests WHERE testName NOT LIKE "%ICP%" ORDER BY testNum'
        tests = db.query(query)
        return tests

    except Exception as e:
        print(f'An error occurred: {e}')
        return None


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

#******************************************************************
#    Table: chemTestsInfo
#******************************************************************

def get_total_chem_info_count(db):
    try:
        query = 'SELECT count(testName) FROM chemTestsInfo'
        count = db.query(query)
        return count[0][0] if count else 0

    except Exception as e:
        print(f'An error occurred: {e}')
        return None

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

#******************************************************************
#    Table: ChemTestsData
#******************************************************************


def addChmTestData(db, sampleNum, testNum, testValue, standardValue, unitValue, jobNum, date):
    try:
        query = 'INSERT INTO chemTestsData (sampleNum, testNum, testValue, standardValue, unitValue, jobNum, creationDate) VALUES (?, ?, ?, ?, ?, ?, ?)'
        db.execute(query, (sampleNum, testNum, testValue, standardValue, unitValue, jobNum, date, ))
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

def checkChmTestsExist(db, sampleNum, testNum, jobNum):
    # Will return 1 if exists, else will return 0
    try:
        query = f"SELECT EXISTS(SELECT 1 FROM chemTestsData WHERE sampleNum = ? AND testNum = ? AND jobNum = ?)"
        db.execute(query, (sampleNum, testNum, jobNum))
        result = db.fetchone()[0]
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

def updateChmTestsData(db, sample_num, test_num, job_num, test_value, standard_value, unit_value):

    # Prepare the SQL UPDATE query
    sql_update_query = """
        UPDATE chemTestsData
        SET testValue = ?, standardValue = ?,unitValue = ?
        WHERE sampleNum = ? AND testNum = ? AND jobNum = ?
    """

     # Values to update
    values = (test_value, standard_value, unit_value, sample_num, test_num, job_num)

    try:
        db.execute(sql_update_query, values)
        db.commit()

        # Check if any rows were updated
        if db.cursor.rowcount > 0:
            print(f"Successfully updated {db.cursor.rowcount} row(s).")
        else:
            print("No rows were updated.")

        return db.cursor.rowcount

    except sqlite3.Error as error:
        print(f"Error occurred: {error}")

        return None

def deleteChmTestDataItem(db, sampleNum, testNum, jobNum):

    query = 'DELETE FROM chemTestsData WHERE sampleNum = ? AND testNum = ? and JobNum = ?'

    try:
        db.execute(query, (sampleNum, testNum, jobNum))
        db.commit()

        # Check how many rows were deleted
        deleted_rows = db.cursor.rowcount  # Get the number of deleted rows
        if deleted_rows > 0:
            print(f"Successfully deleted {deleted_rows} row(s) from chemTestsData.")
        else:
            print("No rows were deleted (the condition may not have matched any records).")

        return deleted_rows

    except Exception as e:
        print(e)

        return None

#******************************************************************
#    Table: icpData
#******************************************************************

def getIcpMachineData(database, jobNumber):
    try:
        query = 'SELECT sampleName, jobNum, data FROM icpData WHERE jobNum = ? ORDER BY sampleName ASC'

        return list(database.query(query, (jobNumber, )))

    except Exception as e:
        print(e)
        return None


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

