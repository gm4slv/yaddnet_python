#!/usr/bin/env python
# purge resolve db table of UNK
import MySQLdb
import time
import pysql

    
    
def purge_db():
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    #sql = "delete from resolve2 where callsign like '%UNK%' or vesseltype like '%n/a%' or mmsi<201000000 or mmsi>775000000 or mmsi REGEXP '0{9,}|1{9,}|2{9,}|3{9,}|4{9,}|5{9,}|6{9,}|7{9,}|8{9,}|9{9,}'"
    sql = "delete from resolve2 where callsign like '%UNK%' or mmsi<201000000 or mmsi>775000000 or mmsi REGEXP '0{9,}|1{9,}|2{9,}|3{9,}|4{9,}|5{9,}|6{9,}|7{9,}|8{9,}|9{9,}'"
#    sql = "delete from resolve2 where mmsi<201000000 or mmsi>775000000 or mmsi REGEXP '0{9,}|1{9,}|2{9,}|3{9,}|4{9,}|5{9,}|6{9,}|7{9,}|8{9,}|9{9,}'"
    
  
    
    cur.execute(sql)
    db.commit()
    db.close()

countbefore = pysql.count_ships()
#pysql.load_logger("PURGE", "Ships in database before purge: %s" % countbefore)
#pysql.load_logger("PURGE", "Pruning Ship Name database")
purge_db()
countafter = pysql.count_ships()
pysql.load_logger("PURGE", "Ships in resolver database after purge: %s (%d deleted)" % (countafter, int(countbefore)-int(countafter)))
