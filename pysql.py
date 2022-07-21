# python MySQL Test file

import MySQLdb
import time

#datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))

def load_logger(ID, text):

    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 

    sql = "INSERT INTO logger (DATETIME, ID, MESSAGE) VALUES (%s, %s, %s);"

    data = (datetime, ID, text)

    # Execute the SQL command
    cur.execute(sql, data)
    # Commit your changes in the database
    db.commit()

    # disconnect from server
    db.close()
    
def load_yaddnet(datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc):

    #load_logger("[UPLOAD]", "PySQL Loading MAIN database")
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "INSERT INTO log (datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    data = (datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc)
    
    cur.execute(sql, data)
    db.commit()
    db.close()

def load_fulllog(datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc):

    #load_logger("[UPLOAD]", "PySQL Loading MAIN database")
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "INSERT INTO full_log (datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    data = (datetime, rx_id, rx_freq, fmt, to_mmsi, cat, from_mmsi, tc1, tc2, freq, pos, eos, ecc)
    
    cur.execute(sql, data)
    db.commit()
    db.close()

    
    
# new_dsc_call = datetime+";"+""+rx_id+";"+rx_freq+";"+fmt+";"+to_mmsi+";"+cat+";"+from_mmsi+";"+tc1+";"+tc2+";"+freq+";"+pos+";"+eos+";"+ecc 


def load_newlog(datetime, rx_id, rx_freq, fmt, cat, tc1, tc2, freq, pos, eos, ecc, raw_to_mmsi, raw_from_mmsi, to_type, from_type, raw_dsc_message, to_mid, from_mid, to_ctry, from_ctry, to_name, from_name):

    #load_logger("[UPLOAD]", "PySQL Loading TEST database")
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "INSERT INTO newlog (datetime, rx_id, rx_freq, fmt, cat, tc1, tc2, freq, pos, eos, ecc, raw_to_mmsi, raw_from_mmsi, to_type, from_type, raw_dsc_message, to_mid, from_mid, to_ctry, from_ctry, to_name, from_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    data = (datetime, rx_id, rx_freq, fmt, cat, tc1, tc2, freq, pos, eos, ecc, raw_to_mmsi, raw_from_mmsi, to_type, from_type, raw_dsc_message, to_mid, from_mid, to_ctry, from_ctry, to_name, from_name)
    
    cur.execute(sql, data)
    db.commit()
    db.close()
    
    
def add_shipname(mmsi, shipname):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "INSERT INTO resolve (mmsi, shipname) VALUES (%s, %s);"
    
    data = (mmsi, shipname)
    
    cur.execute(sql, data)
    db.commit()
    db.close()

def check_mmsi(mmsi):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT shipname from resolve where mmsi = %s" % mmsi 
    
    
    cur.execute(sql)
    shipname = cur.fetchone()
    db.close()
    return shipname
    
def check_uploader(rxid):
    print "IN PYSQL CHECK UPLOADER ", rxid
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT name from uploaders where rxid = '%s'" % (rxid)
    
    
    cur.execute(sql)
    uploader = cur.fetchone()
    print "in check_uploader with %s : %s" % (rxid, uploader)
    db.close()
    return uploader
    
def check_mmsi2(mmsi):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT shipname, callsign, vesseltype from resolve2 where mmsi = %s" % mmsi 
    
    
    cur.execute(sql)
    shipname = cur.fetchone()
    print "in check_mmsi2 with %s : %s" % (mmsi, shipname)
    db.close()
    return shipname

def add_shipname2(mmsi, shipname, callsign, vesseltype):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "INSERT INTO resolve2 (mmsi, shipname, callsign, vesseltype) VALUES (%s, %s, %s, %s);"
    
    data = (mmsi, shipname, callsign, vesseltype)
    
    cur.execute(sql, data)
    db.commit()
    db.close()    
    
def count_ships():
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT count(*) from resolve2"
    
    
    cur.execute(sql)
    count = cur.fetchone()[0]
    
    db.close()
    return count
    
def count_unk():
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT count(*) from resolve2 where callsign like '%UNK%'"
    
    
    cur.execute(sql)
    count = cur.fetchone()[0]
    
    db.close()
    
    return count
    
    
def count_na():
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT count(*) from resolve2 where vesseltype like '%n/a%'"
    
    
    cur.execute(sql)
    count = cur.fetchone()[0]
    
    db.close()
    return count

def count_mod(drop):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    cur = db.cursor()
   
    sql = "SELECT count(*) from newlog where datetime>date_sub(now(), interval 7 day) and RX_ID='%s' " % drop

    cur.execute(sql)
    count = cur.fetchone()[0]
    
    db.close()
    
    return count

def check_coast(mmsi):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT coastname from coast where mmsi = %s" % mmsi 
    
    
    cur.execute(sql)
    coastname = cur.fetchone()
    print "check_coast with %s : %s" % ( mmsi, coastname)
    db.close()
    return coastname

def check_mid(mid):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT ctry from mid where mid = %s" % mid
    
    
    cur.execute(sql)
    ctry = cur.fetchone()
    print "check_mid with %s : %s" % (mid, ctry)
    db.close()
    return ctry


def check_special(mmsi):
    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    
    cur = db.cursor()
    
    sql = "SELECT coastname from special where mmsi = %s" % mmsi
    
    
    cur.execute(sql)
    coastname = cur.fetchone()
    print "check_special with %s : %s" % (mmsi, coastname)
    db.close()
    return coastname


