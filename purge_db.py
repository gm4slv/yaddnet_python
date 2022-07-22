#!/usr/bin/env python
# DB Purge script

import MySQLdb
import time

import pysql
purge_commands = open("/home/gm4slv/yaddnet/purge_commands.txt", 'r')


def purge_db_func(command):

    db = MySQLdb.connect(host="localhost", user="root", db="yadd") 
    

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 



 

    # Execute the SQL command
    cur.execute(command)
    # Commit your changes in the database
    db.commit()

    # disconnect from server
    db.close()

pysql.load_logger("PURGE", "Purging main databases of errors & old logger entries" )


for line in purge_commands:
    
    #pysql.load_logger("PURGE", line)
    purge_db_func(line)
    
pysql.load_logger("PURGE", "Main database purge complete" )
