import sqlite3 

def connectDatabase(dbLocation): 
    con = sqlite3.connect(dbLocation)
    
    return con 



