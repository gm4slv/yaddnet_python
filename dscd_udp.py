#!/usr/bin/env python

import SocketServer
import socket
import threading
import re
import PyYadd
import pysql
import time
import datetime


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        print data
        

        self.make_dsc(data)
        
        
    def make_dsc(self, data):
        group_call = False
        fmt = ""
        cat_dict = { "(safety)": "SAF", "(routine)" : "RTN", "(urgency)" : "URG", "(distress)" : "DIS" }
        data = "".join(x for x in data if ord(x) < 128 and ord(x) > 31)
        dsc_call = data.split(";")
        #print dsc_call
       
        rx_freq = dsc_call[0]
        rx_freq_list = rx_freq.split()
        
        rx_id = rx_freq_list[0]

        rx_id = rx_id[0:18]
        pysql.load_logger("UDP", "%s : %s" % (rx_id, self.client_address[0]))        
         
            
        rx_freq = rx_freq_list[1]
        
        if rx_freq == "156.525":
            print "VHF DSC Channel 70"
            rx_freq = "156525.0"
        
        if rx_freq == "156525":
            print "VHF Channel 70"
            rx_freq = "156525.0"


        to = dsc_call[1]
        to_list = to.split()
        #print to_list
        
        if to_list[0] == "area":
            fmt = "AREA"
            #to_string = to_list[0].upper() + " " + to_list[2] + " " + to_list[3]
            
            vert = list(to_list[2])
            hor = list(to_list[3])
            ns = vert[0]
            ew = hor[0]
            
            vc = vert[1] + vert[2]
            hc = hor[1] + hor[2] + hor[3]
            
            vs = vert[5] + vert[6]
            hs = hor[6] + hor[7]
            
            box = vc + chr(176) + ns + "=>" + vs + chr(176) + " " + hc + chr(176) + ew + "=>" + hs + chr(176)
            
            to_mmsi = "AREA" + " " + box
            
        elif to_list[0] == "all":
            fmt = "ALL"
            to_mmsi = "ALL SHIPS"
        elif to_list[0] == "group":
            fmt = "GRP"
            to_mmsi = to_list[1]
            if to_mmsi[0] == "0" and to_mmsi[1] != "0": # a group callsign
                group_call = True
                print "To a Group ", to_mmsi
                to_mmsi = "GROUP,"+to_mmsi
        elif to_list[0] == "DISTRESS":
            fmt = "DIS"
            to_mmsi="DISTRESS"
            
        else:
            fmt = "SEL"
            to_mmsi = to
            
        cat_text = dsc_call[2]
        try:
            cat = cat_dict[cat_text]
        except:
            cat = "UNK"
         
        from_mmsi = dsc_call[4]
        
        if from_mmsi[0:2] == "00": # coast station
            print "from coast station ", from_mmsi
            from_mmsi = "COAST,%s" % from_mmsi
            
        elif from_mmsi[0] == "0" and from_mmsi[1] != "0": # group callsign
            print "from a group", from_mmsi
            from_mmsi = "GROUP,"+from_mmsi
        else:
            print "from Ship ", from_mmsi
            from_mmsi = "SHIP,"+from_mmsi
         
      
        if to_mmsi[0:2] == "00":
            print "to coast station ", to_mmsi
            to_mmsi = "COAST,%s" % to_mmsi

        elif to_mmsi[0] == "0" and to_mmsi[1] != "0" : # group callsign
            print "to a group", to_mmsi
            to_mmsi = "GROUP,"+to_mmsi
            group_call = True

        elif fmt != "ALL" and fmt != "AREA" and group_call != True and fmt != "DIS":
            #print "we don't have ALL or AREA or GROUP"
            print "To Ship ", to_mmsi
            to_mmsi = "SHIP,"+to_mmsi 
   
            
        tc1_data_eos = dsc_call[5].split()
        #print tc1_data_eos
        
        tc1 = tc1_data_eos[0].upper()
        if tc1 == "NO":
            tc1 = "NOINF"
        elif tc1 == "J3":
            tc1 = "J3E TP"
        elif tc1 == "F3":
            tc1 = "F3E/G3E"
        elif tc1 == "F3dup":
            tc1 = "F3E/G3E, Duplex TP"
        elif tc1 == "UNABLE":
            tc1 = "UNABLE TO COMPLY"
        elif tc1 == "F1FEC":
            tc1 = "F1B/J2B TTY-FEC"
        elif tc1 == "F1ARQ":
            tc1 = "F1B/J2B TTY-ARQ"
        elif tc1 == "POLLING":
            tc1 = "POLL"
        elif tc1 == "POSITION":
            tc1 = "POSUPD"
        
        if tc1_data_eos[1] != tc1_data_eos[-1]:
        
            pos_freq = tc1_data_eos[1]
            
            # we have some pos/freq data
            if tc1_data_eos[0] == "telecommands":
                freq = "--"
                pos = "--"
                tc1 = "UNK"
                
            elif tc1_data_eos[1] == "posn":
                #print "we have a posit - TC1 != Position"
                freq = "--"
                latd_in = list(tc1_data_eos[2])
                longd_in = list(tc1_data_eos[4])
                
                ns = latd_in[0]
                ew = longd_in[0]
                
                lat_d = latd_in[1] + latd_in[2]
                long_d = longd_in[1] + longd_in[2] + longd_in[3]
                
                latm_in = list(tc1_data_eos[3])
                longm_in = list(tc1_data_eos[5])
                
                lat_m = latm_in[0]+latm_in[1]
                long_m = longm_in[0] + longm_in[1]
                
                latitude = lat_d + "." + lat_m + chr(176) + ns
                longitude = long_d + "." + long_m + chr(176) + ew
                pos = latitude + " " + longitude
                #pos = tc1_data_eos[2] + chr(176) + tc1_data_eos[3] + " " + tc1_data_eos[4] + chr(176) + tc1_data_eos[5]  
                
            elif tc1_data_eos[0] == "Position":
                #print "we have a posit - TC1 = Position"
                freq = "--"
                latd_in = list(tc1_data_eos[1])
                longd_in = list(tc1_data_eos[3])
                
                ns = latd_in[0]
                ew = longd_in[0]
                
                lat_d = latd_in[1] + latd_in[2]
                long_d = longd_in[1] + longd_in[2] + longd_in[3]
                
                latm_in = list(tc1_data_eos[2])
                longm_in = list(tc1_data_eos[4])
                
                lat_m = latm_in[0]+latm_in[1]
                long_m = longm_in[0] + longm_in[1]
                
                latitude = lat_d + "." + lat_m + chr(176) + ns
                longitude = long_d + "." + long_m + chr(176) + ew
                pos = latitude + " " + longitude
                #pos = tc1_data_eos[1] + chr(176) + tc1_data_eos[2] + " " + tc1_data_eos[3] + chr(176) + tc1_data_eos[4]
           
            elif "kHz" in pos_freq:
                #print "we have a freq"
                freq=re.sub('kHz/', '/',pos_freq)
                freq = re.sub('kHz', 'KHz', freq)
                freq = re.sub('/no', 'KHz', freq)
                freq = re.sub('ch', 'CH', freq)
                pos = "--"
                
            elif "ch" in pos_freq:
                #print "we have channel no.s"
                freq = re.sub('ch', 'CH', pos_freq)
                freq=re.sub('kHz/', '/',freq)
                freq = re.sub('/no', '', freq)
                freq = re.sub('kHz', 'KHz', freq)
                pos = "--"
                
            elif "no" in tc1_data_eos:
                #print "no freq"
                freq = "--"
                pos = "--"
            elif "unable" in tc1_data_eos:
                #print "unable"
                freq = "--"
                pos = "--"
        else:
            #print "else...."
            pos_freq = "--"
            pos = "--"
            freq = "--"
        eos = tc1_data_eos[-1]
        datestamp = (datetime.datetime.utcnow() - datetime.timedelta(seconds=4)).strftime("%Y-%m-%d %H:%M:%S")
        
        tc2 = "--"
        ecc = "ECC --- OK"
        
        yadd_message = datestamp+";"+rx_id+";"+rx_freq+";"+fmt+";"+to_mmsi+";"+cat+";"+from_mmsi+";"+tc1+";"+tc2+";"+freq+";"+pos+";"+eos+";"+ecc
        print yadd_message
        
        #self.write_file(yadd_message)
        pysql.load_logger("dUDPSERV", "DSC Decoder message added : %s" % (yadd_message))
        
        #PyYadd.send_to_mirror(yadd_message)

        PyYadd.make_dsc_call(data,yadd_message)
        return
        
 
class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

if __name__ == "__main__":
    pysql.load_logger("dUDPSERV", "Starting DSCDecoder UDP interface....")
    HOST, PORT = "", 4530

    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
    ip, port = server.server_address
    server.serve_forever()
    # Start a thread with the server -- 
	# that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    server.shutdown()
