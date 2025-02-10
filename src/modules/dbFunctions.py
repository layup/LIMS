



def getFrontHistory(db):
    query = 'SELECT jobNumber, companyName, creationDate, status FROM history'
    db.execute(query)

    jobNumbers = db.fetchall()
    return  [item[0] for item in jobNumbers]
