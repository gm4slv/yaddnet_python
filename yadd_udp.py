#!/usr/bin/env python

import SocketServer
import socket
import threading
import re

import PyYadd
import pysql
import time


  
    
class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
   

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        

        pysql.load_logger("UDP", "%s : %s" % (data.split(";")[0][1:-1], self.client_address[0]))
        
        self.dsc_list = self.make_dsc(data)
    
    
        
    def make_dsc(self,dsc_message):
        print "\n\n**************\nUDP Message %s \r\n" % dsc_message
        if "~" in dsc_message:
            print "\nParity Error. Message Discarded\r\n"
            print "*****************\n\n"
            pysql.load_logger("yUDPSERV", "Parity error, discarded : %s" % ( dsc_message))

            return

        dsc_list = dsc_message.split(";")
        
        
        
        
            
        #print dsc_list
        
        # rx_id comes from YaDD as "[john_fcdpp]"
        # we need to discard the 1st and last char. "[" and "]"
        # slicing with [1:-1] does this
        
        # Also...consider curtailing to 18 chars? YaDD tells user to use up to 18 chars
        # some users make long RX_IDs. SQL table allows 30 for the RX_ID field
        # but curtailing might discourage them from using > 18 ?
        rx_id = dsc_list[0][1:-1]

	rx_id = rx_id[0:19]
        
        if rx_id == "":
            pysql.load_logger("yUDPSERV", "Empty RX ID, message discarded : %s" % (dsc_message))
            return

        rx_id = "".join(x for x in rx_id if ord(x) != 35 and ord(x) != 43)

        
        
        rx_freq = dsc_list[1]
        #print rx_id
        
        
        #print "rx_freq raw ", rx_freq
        
        rx_freq = rx_freq[-7:]
        
        rx_freq = "".join(x for x in rx_freq if ord(x) < 58 and ord(x) > 45)
        
        # trap events where the rx_freq word has a ";" character in its leading bytes
        # which causes the split() to choose the wrong fields
        
       
        fmt = dsc_list[2]
        
        to_mmsi = dsc_list[3]
        
       
            
        if fmt == "DIS" or fmt == "ALL":
            #print "\r\nALL ALL ALL.......\r\n"
            to_mmsi = "ALL SHIPS"
            
        elif fmt == "AREA":
            pass
            #print "\r\nAREA CALL\r\n"
            #to_mmsi = to_mmsi  
        
        elif to_mmsi[0:2] == "00":
            to_mmsi = "COAST,%s" % to_mmsi
        
        elif to_mmsi[0] == "0" and to_mmsi[1] != "0":
            to_mmsi = "GROUP,"+to_mmsi
        
        else:# to_mmsi[0] != "0":
            to_mmsi = "SHIP,"+to_mmsi
           
            
        cat = dsc_list[4]
      
        from_mmsi = dsc_list[5]
        
        if from_mmsi[0:2] == "00": # coast station
            from_mmsi = "COAST,%s" % from_mmsi
            
        elif from_mmsi[0] == "0" and from_mmsi[1] != "0": # group callsign
            #print "from a group", from_mmsi
            from_mmsi = "GROUP,"+from_mmsi
        else:
            #print "from Ship ", from_mmsi
            from_mmsi = "SHIP,"+from_mmsi
        
        tc1 = dsc_list[6]
        tc2 = dsc_list[7]
        freq = dsc_list[8]
        pos = dsc_list[9]
        eos = dsc_list[10]
        
        ecc = dsc_list[11]
        
        ecc_ok = ecc.split()[-1]
        
        if ecc_ok == "ERR":
            print "\r\n\nECC Error\nMessage discarded\n******************\n\n"
            pysql.load_logger("yUDPSERV", "ECC error, discarded : %s" % ( dsc_message))
            return

        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        
        yadd_message = datetime+";"+rx_id+";"+rx_freq+";"+fmt+";"+to_mmsi+";"+cat+";"+from_mmsi+";"+tc1+";"+tc2+";"+freq+";"+pos+";"+eos+";"+ecc
        print "UDP input converted to Yadd message:\n %s \n" % yadd_message
        print "*****************\n\n"
        pysql.load_logger("yUDPSERV", "YaDD message added :  %s" % (yadd_message))
        #PyYadd.send_to_mirror(yadd_message)
        PyYadd.make_dsc_call(dsc_message,yadd_message)
        return
 
class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

if __name__ == "__main__":
    pysql.load_logger("yUDPSERV", "Starting YaDD UDP interface....")
    HOST, PORT = "", 50666

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
