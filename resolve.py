
import json
import urllib
import urllib2
import re
import time
from class_dict import *

import pysql


def write_resolve_log(text):
    filename = '/var/www/html/pages/php/test/logfile.txt'
    f = open(filename, 'a+')  # a+ is "append to file, create it if it doesn't exist"
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    id = "RESOLVER"
    log = ";".join((timenow, id))
    entry = ";".join((log, text))
    #print entry
    f.write(entry+'\r\n')
    f.close()




def resolve_mmsi(mmsi):
    
    # first test if it's a valid 9-digit MMSI
    if len(mmsi) != 9:
        name_call = mmsi + ", UNK, N/A"
        #write_resolve_log("")
        #write_resolve_log("Illegal length of MMSI %s = %i chars" % (mmsi, len(mmsi)))
        pysql.load_logger("RESOLVER", "Illegal length of MMSI %s = %i chars" % (mmsi, len(mmsi)))
	return name_call
    
    # check if the MMSI has a valid MID, otherwise return it as MMSI for PyYadd to check itself
    
    
    try:

        mid = mmsi[0:3]
        ctry = pysql.check_mid(mid)
        if ctry != None:
            #ctry = mid_dict[mid]
            print "Valid MID...."
        else:
            pysql.load_logger("RESOLVER", "MMSI %s has no valid MID %s" % (mmsi, mid))
            return mmsi

    except:
        #write_resolve_log("")
        #write_resolve_log("MMSI %s has no valid MID %s" % (mmsi, mid))
        pysql.load_logger("RESOLVER", "MMSI %s has no valid MID %s" % (mmsi, mid))
        return mmsi
       
       
    # test for 9-digit-the-same MMSIs - intention is to bypass the Resolving
    # when one is detected
    if re.search(r'0{9,}|1{9,}|2{9,}|3{9,}|4{9,}|5{9,}|6{9,}|7{9,}|8{9,}|9{9,}', mmsi):
        print "TEST***Bogus MMSI", mmsi
        #write_resolve_log("TEST***Bogus MMSI %s" % mmsi)
        pysql.load_logger("RESOLVER", "TEST***Bogus MMSI %s" % mmsi)
        name_call = mmsi+", UNK, N/A"
        return name_call
        
    # look up the mmsi provided in the dictionary    
    try:
        ship = pysql.check_mmsi2(mmsi)
        #print "Checking database ", ship
        
        name = ship[0].upper().lstrip()
        call = ship[1].lstrip()
        vt = ship[2].lstrip()
        
        #name_call = mmsi_dict[mmsi]
        name_call = name+", "+call+", "+vt
        
        #write_resolve_log("Name already known for %s = %s" % (mmsi, name_call))
        #pysql.load_logger("RESOLVER", "Name already known for %s { %s}" % (mmsi, name_call))
        
        
        return name_call
    
    # not found - we need to try the resolution methods in turn
    except:
    
        # call each resolution method in turn until a name_call is found
        #write_resolve_log("")
        #write_resolve_log("Trying aprs.fi for %s" % mmsi)
        pysql.load_logger("RESOLVER", "Trying aprs.fi for %s" % mmsi)
        name_call = resolve_aprs(mmsi)
        if name_call != None:
            pysql.load_logger("RESOLVER", "Found at aprs.fi {%s : %s}" % (mmsi, name_call))
        elif name_call == None:
            #write_resolve_log("")
            #write_resolve_log("Trying Marine Traffic for %s" % mmsi)
            
            
            #pysql.load_logger("RESOLVER", "Trying Marine Traffic for %s" % mmsi)
            #name_call = resolve_marine(mmsi)
            name_call = None

            if name_call != None:
                pysql.load_logger("RESOLVER", "Found at Marine Traffic {%s : %s}" % (mmsi, name_call))
            elif name_call == None:
            # we're stuck
                #write_resolve_log("")
                #write_resolve_log("Nothing found. We will use mmsi %s" % mmsi)
                    
                pysql.load_logger("RESOLVER", "Nothing found for MMSI %s" % mmsi)
                name_call = mmsi + ", UNK, N/A"


        
        
        pysql.load_logger("RESOLVER", "Adding new record to ship database : %s { %s }" % (mmsi, name_call))
        
        
        try:
            name = name_call.split(',')[0].lstrip()
            call = name_call.split(',')[1].lstrip()
            vesseltype = name_call.split(',')[2].lstrip()
            if mmsi != name:
                pysql.add_shipname2(mmsi, name, call, vesseltype)
            else:
                pysql.add_shipname2(mmsi, name, call, vesseltype)
        except:
            
            pass
        
        
    return name_call
            
def resolve_aprs(mmsi):
    
        url = "http://api.aprs.fi/api/get?apikey=49022.741rOwWQ5ato0Y&name="+mmsi+"&what=loc&format=json"
        
        req = urllib2.Request(url)

        req.add_header('User-agent', 'YaDDNet DSC (+http://gm4slv.plus.com:8000)')
        
        # delay each lookup to prevent overloading the API
        time.sleep(1)
        #write_resolve_log("")
        #write_resolve_log("Looking up %s at aprs.fi" % mmsi)
        #pysql.load_logger("RESOLVER", "Looking up %s at aprs.fi" % mmsi)

        response = urllib2.urlopen(req)

        
        #response = urllib.urlopen(url);
        data = json.loads(response.read())
        #print data
        try:
            entry =  data['entries']
        except:
                
            # APRS.FI has refused to provide data 
            # return "None" to the calling function so that
            # the next resolution method can be tried
            return None
            
        try:
            # parse the json-derived dictionary to extract "name", "mmsi" (although we know this already)
            # and vclass
            
            station = entry[0]
            name = station['name'].upper().replace(',', '').strip()
            #name = station['name'].title().replace(',', '').strip()
            #print "Name....", name
            mmsi = station['mmsi']
            call = station['srccall']
            vclass = station['vesselclass']
            
            # vclass is the AIS digits
            # look up in the class_dict to convert to a text vessel type
            try:
                vesseltype = class_dict[vclass]
                
            # the number doesn't match anything in the dictionary, use the number instead
            except:
                vesseltype = vclass
               
            # name_call is a single string : "name, call, vesseltype"
            
            name_call = name + ", " + call + ", " + vesseltype

            print "New Details : %s :  %s" % (mmsi, name_call)
            if call != mmsi:

                #write_resolve_log("New MMSI found at aprs.fi: %s : %s" % (mmsi, name_call))
             	#pysql.load_logger("RESOLVER", "New MMSI found at aprs.fi: %s : %s" % (mmsi, name_call))
                print name_call
                # send back the name_call string
                return name_call
            else:
                #write_resolve_log("aprs.fi provided call %s = mmsi %s. Ignoring result" % (call, mmsi))
                pysql.load_logger("RESOLVER", "bogus aprs.fi record")
                return None
        
        # although we got a json reply, it doesn't contain the name/call etc.
        # we will send back "None" to trigger the next resolution metho
        except:
            print "Not Found at APRS.FI %s " % mmsi
            #write_resolve_log("Not found at aprs.fi: %s" % mmsi)
            pysql.load_logger("RESOLVER", "Not found at aprs.fi: %s" % mmsi)
           
            return None

            
def resolve_marine(mmsi):
    url = "http://www.marinetraffic.com/en/ais/index/search/all?keyword="+mmsi
        
    req = urllib2.Request(url)

    req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
    #write_resolve_log("")    
    #write_resolve_log("Looking up %s at Marine Traffic" % mmsi)
    #pysql.load_logger("RESOLVER", "Looking up %s at Marine Traffic" % mmsi)
    
    response = urllib2.urlopen(req)
    data = response.read()
    #print data
    try:
        name_line = re.findall(mmsi+'.*\[', str(data))
        #print "***MT ", name_line
        name_list = name_line[0].split(' ')
        #print "***MT ", name_list
        if name_list[-1] == "[":
            name_list.pop()
            #print name_list
            
        name = " ".join(name_list[1:])[1:].upper().replace(',', '').strip()
        #name = " ".join(name_list[1:])[1:].title().replace(',', '').strip()
        
        # MT web page only gives the NAME, so we need to add UNK and N/A for call
        # and Vessel Type - this will allow the mmsi_dict purge to remove the mapping
        # at intervals, to cause a new lookup - hopefully a better match will be 
        # found at a later date
        
        name_call = name + ", UNK, N/A"
        
        print name_call
        #write_resolve_log("New MMSI found at Marine Traffic: %s : %s" % (mmsi, name_call))
        #pysql.load_logger("RESOLVER", "New MMSI found at Marine Traffic: %s : %s" % (mmsi, name_call))
        
        return name_call
        
    except:
        # Not Found, return None to trigger next resolution method
        print "Not Found at Marine Traffic %s " % mmsi
        #write_resolve_log("Not found at Marine Traffic: %s" % mmsi)
        pysql.load_logger("RESOLVER", "Not found at Marine Traffic: %s" % mmsi)
        
        return None



def resolve_itu(mmsi):
    pysql.load_logger("RESOLVER", "Not tried at ITU: %s" % mmsi)

    return None

 
  
