# development version for new Ship Resolution process

#import json
import time
from resolve import *
import socket

import pysql

import sys

reload(sys)
sys.setdefaultencoding("windows-1252")

def send_to_mirror(data):
    log_data = "[log];"+data
    port = 2505
    host = "216.108.227.44"
    host2 = "80.229.223.86"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(log_data, (host, port))
    sock.sendto(data, (host2, port))
    
    return


def make_dsc_call(dsc_message, line):
    to_special_flag = False
    from_special_flag = False

    print "+++++++++++++++++ IN PyYaDD"
    raw_dsc_message = dsc_message
    dsc_list = line.split(';')
    #print dsc_list
    datetime = dsc_list[0]
    rx_id = dsc_list[1]
    rx_freq = dsc_list[2]
    fmt = dsc_list[3]
    to_mmsi_raw = dsc_list[4]
    cat = dsc_list[5]
    from_mmsi_raw = dsc_list[6]
    tc1 = dsc_list[7]
    tc2 = dsc_list[8]
    freq = dsc_list[9]
    pos = dsc_list[10]
    eos = dsc_list[11]
    ecc = dsc_list[12].split()[-1]
    to_mmsi_list = to_mmsi_raw.split(',')
    from_mmsi_list = from_mmsi_raw.split(',')

    
    # Deal with special cases
    
    if to_mmsi_list[0] == "SHIP": 
        print "TESTING FOR SPECIALS in TO..........................." 
        
        to_special_name = pysql.check_special(to_mmsi_list[1])
        
        if to_special_name != None:
            to_mmsi_list[0] = "COAST"
            to_special_flag=True
            pysql.load_logger("LOGGER", "Found a special: %s" % to_mmsi_list[1])
        else:
            to_special_flag=False


    if from_mmsi_list[0] == "SHIP":
        print "TESTING FOR SPECIALS in FROM.........................."
        
        from_special_name = pysql.check_special(from_mmsi_list[1])

        if from_special_name != None:
            from_mmsi_list[0] = "COAST"
            from_special_flag=True
            pysql.load_logger("LOGGER", "Found a special: %s" % from_mmsi_list[1])
        else:
            from_special_flag=False

        
    if to_mmsi_list[0] == "COAST":
        print "Testing for 000000000 in TO"
        if to_mmsi_list[1] == "000000000":       
            to_mmsi_list[0] = "SHIP"
        
    if from_mmsi_list[0] == "COAST":
        print "Testing for 000000000 in FROM"
        if from_mmsi_list[1] == "000000000":       
            from_mmsi_list[0] = "SHIP"
            
    else:
        pass
        
    
    ###
    ## TO TO TO TO TO 
    ##
    if to_mmsi_list[0] == "COAST":
        print "We have coast"
        to_mmsi = to_mmsi_list[1]
        print "Coast TO MMSI: ", to_mmsi
        to_type = "COAST" 
        raw_to_mmsi = to_mmsi
        print "to_special_flag ", to_special_flag
        try:
            name = pysql.check_coast(to_mmsi)
            
            ############################
            if not name:
                name = "UNID"
            else:
                pass
            print "TO Name : ", name
            
            # If SPECIAL use first 3 digis as MID 
            if to_special_flag==True:
            
                mid = to_mmsi[0:3]
            # otherwise a normal COAST use digits 3,4,5
            else:              
                mid = to_mmsi[2:5]
            print "TO mid ", mid
           
            ctry = pysql.check_mid(mid)
            if not ctry:
                ctry = "UNK"
            else:
                pass


            to_mid = mid
            to_ctry = ctry
            to_name = name
            to_newlog = to_mmsi
        
        except:
            pysql.load_logger("PyYaDD", "Exception in TO COAST : %s" % raw_dsc_message)

        

            
    elif to_mmsi_list[0] == "SHIP":
        to_mmsi = to_mmsi_list[1]
        to_type = "SHIP"
        raw_to_mmsi = to_mmsi
        if "~" not in to_mmsi and to_mmsi[0] != "0":
            to_name_call = resolve_mmsi(to_mmsi)
            print "Name", to_name_call
        else:
            to_name_call = to_mmsi
        try:
            mid = to_mmsi[0:3]
            
            ctry = pysql.check_mid(mid)
            if not ctry:
                ctry = "UNK"
            else:
                pass

            to_mid = mid
            to_ctry = ctry
            to_name = to_name_call
            to_newlog = to_mmsi
        
        except:
            pysql.load_logger("PyYaDD", "Exception in TO SHIP : %s" % raw_dsc_message)
        

    else:
        to_newlog = to_mmsi_raw
        to_mmsi = to_mmsi_raw
        to_mmsi2 = to_newlog
        
        raw_to_mmsi = to_mmsi_raw
        if fmt == "ALL":
            to_type = "ALL"
            to_mid = "--"
            to_ctry = "--"
            raw_to_mmsi = ""
            to_name = "ALL SHIPS"
        elif fmt == "AREA":
            to_type = "AREA"
            to_mid = "--"
            to_ctry = "--"
            to_name = "AREA"
        else:
            to_type = "UNK"
            to_mid = "UNK"
            to_ctry = "UNK"
            to_name = "UNID"


    ######### GROUP GROUP #####################
    #
    #
    if to_mmsi_list[0] == "GROUP":
        to_type = "GROUP"
        to_mmsi = to_mmsi_list[1]
        raw_to_mmsi = to_mmsi
        print "We have TO GROUP"
        try:
            mid = to_mmsi[1:4]
            print mid
            ctry = pysql.check_mid(mid)
            if not ctry:
                ctry = "UNK"
            else:
                pass
            
            to_mid = mid
            to_ctry = ctry
            to_name = to_mmsi

            to_newlog = to_mmsi
        
        except:
            pysql.load_logger("PyYaDD", "Exception in TO GROUP : %s" % raw_dsc_message)
        


            
    ####
    ###
    ## FROM FROM FROM FROM
    ##
    ##

    if from_mmsi_list[0] == "COAST":
        from_type = "COAST"
        print "We have coast"
        from_mmsi = from_mmsi_list[1]
        raw_from_mmsi = from_mmsi
        print "COAST FROM MMSI :", from_mmsi
        print "from_special_flag ", from_special_flag
        try:
            name = pysql.check_coast(from_mmsi)
            
            if not name:
                name = "UNID"
            else:
                pass

            print "FROM Name :", name
            if from_special_flag==True:
            
                mid = from_mmsi[0:3]
            else:              
                mid = from_mmsi[2:5]
                
            print "From MID :", mid
            
            ctry = pysql.check_mid(mid)
            if not ctry:
                ctry = "UNK"
            else:
                pass

            from_mid = mid
            from_ctry = ctry
            from_name = name
            from_newlog = from_mmsi
        
        except:
            pysql.load_logger("PyYadd", "Exception in FROM COAST : %s" % raw_dsc_message)


    elif from_mmsi_list[0] == "SHIP":
        from_type = "SHIP"
        from_mmsi = from_mmsi_list[1]
        raw_from_mmsi = from_mmsi
        print "From MMSI", from_mmsi
        if "~" not in from_mmsi and from_mmsi[0] != "0":
            from_name_call = resolve_mmsi(from_mmsi)
            print "Name", from_name_call
        else:
            from_name_call = from_mmsi
            
        try:
            mid = from_mmsi[0:3]
                
            ctry = pysql.check_mid(mid)
            if not ctry:
                ctry = "UNK"
            else:
                pass
            
            from_mid = mid
            from_ctry = ctry
            from_name = from_name_call
            from_newlog = from_mmsi 
        
        except:
            pysql.load_logger("PyYadd", "Exception in FROM SHIP : %s" % raw_dsc_message) 
        

    else:
        from_mid = "UNK"
        from_ctry = "UNK"
        from_name = "UNID"

        from_mmsi = from_mmsi_raw
        raw_from_mmsi = from_mmsi
        from_mmsi2 = from_mmsi_raw
        from_type = "UNK"
    
    ######### GROUP GROUP #####################
    #
    #
    if from_mmsi_list[0] == "GROUP":
        from_type = "GROUP"
        from_mmsi = from_mmsi_list[1]
        raw_from_mmsi = from_mmsi
        print "We have TO GROUP"
        try:
            mid = from_mmsi[1:4]
            
            ctry = pysql.check_mid(mid)
           
            if not ctry:
                ctry = "UNK"
            else:
                pass
            
            from_mid = mid
            from_ctry = ctry
            from_name = from_mmsi

            from_newlog = from_mmsi
        
        except:
            pysql.load_logger("PyYadd", "Exception in FROM GROUP : %s" % raw_dsc_message)

    
    new_dsc_call = datetime+";"+""+rx_id+";"+rx_freq+";"+fmt+";"+to_mmsi+";"+cat+";"+from_mmsi+";"+tc1+";"+tc2+";"+freq+";"+pos+";"+eos+";"+ecc
    
    to_name_str = ''.join(to_name)
    from_name_str = ''.join(from_name)

    data_for_mirror = datetime+";"+rx_id+";"+rx_freq+";"+fmt+";"+raw_to_mmsi+";"+to_type+";"+to_mid+";"+to_ctry[0]+";"+to_name_str+";"+cat+";"+raw_from_mmsi+";"+from_type+";"+from_mid+";"+from_ctry[0]+";"+from_name_str+";"+tc1+";"+tc2+";"+freq+";"+pos+";"+eos+";"+ecc+"\r\n"    
    
    send_to_mirror(data_for_mirror)
    
    try:
        pysql.load_newlog(datetime, rx_id, rx_freq, fmt, cat, tc1, tc2, freq, pos, eos, ecc, raw_to_mmsi, raw_from_mmsi, to_type, from_type, raw_dsc_message, to_mid, from_mid, to_ctry, from_ctry, to_name, from_name)
    
    except:
        pysql.load_logger("PyYadd", "Exception in adding new message to database : %s" % new_dsc_call)

    print "**************\n\n\n"        
    return 

    
    
