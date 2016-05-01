import socket
import sys
import os
import json
import ConfigParser
import urllib
import filecmp
import time
import datetime
import shutil
import logging
import logging.handlers




from pprint import pprint


#
# These module-level variables are now captured in a config file. 
#
# door_user = "hackerdoor"
# rootdir = '/home/{0}'.format(door_user)
# uds_address = '{0}/doorsock'.format(rootdir);
# json_dir = '{0}/json'.format(rootdir);
#


config = ConfigParser.ConfigParser()

my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)

handler = logging.handlers.SysLogHandler(address = '/dev/log')
my_logger.addHandler(handler)


def make_paths():
    # Make the directories if we don't already have them.
    #
    #
    
    if not os.path.exists(config.get('paths','rootdir')):
        my_logger.info("hackerdoor: created root working directory '{0}'  ".format(config.get('paths','rootdir')))
        os.makedirs(config.get('paths','rootdir'))


    if not os.path.exists(config.get('paths','json_dir')):
        my_logger.info("hackerdoor: created JSON directory '{0}'  ".format(config.get('paths','json_dir')))
        os.makedirs(config.get('paths','json_dir'))
        


def read_acl():
    for version in [0]:
        json_file = config.get('paths','json_file')
        json_data=open(json_file)
        data = json.load(json_data)
        json_data.close()
        # pprint(data)
        return(data)



def read_config():
    config.read(['/etc/hackerdoor.cfg','hackerdoor.cfg'])


def start_listening_uds():

    uds_address = config.get('paths','uds_address')

    # Make sure the socket does not already exist
    try:
        os.unlink(uds_address)
    except OSError:
        if os.path.exists(uds_address):
            raise
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    print >>sys.stderr, 'starting up on %s' % uds_address
    sock.bind(uds_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    acl = read_acl()
                    if data in acl.keys():
                        my_logger.info("hackerdoor:{2} admitted '{0}' ({1}) ".format(acl[data]['user_id'],acl[data]['name'],config.get('identity','location')))
                        response = "Sure, why not"
                    else:
                        my_logger.info("hackerdoor:{1} rejected '{0}'  ".format(data,config.get('identity','location')))
                        response = "Away with you!"
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(response)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
            
        finally:
            # Clean up the connection
            connection.close()



def knock_uds(message='0303030303'):

    uds_address = config.get('paths','uds_address')

# Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    print >>sys.stderr, 'connecting to %s' % uds_address
    try:
        sock.connect(uds_address)
    except socket.error, msg:
        print >>sys.stderr, msg
        sys.exit(1)

    try:
        # Send data
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)

        amount_received = 0
        amount_expected = len(message)
    
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()




def update_access():

    jsonfile = config.get('paths','json_file');

    target = config.get('url','acl_download');

    tempfile, headers = urllib.urlretrieve(target)

    temp_data=open(tempfile)
    worked = True

    try:
        data = json.load(temp_data)
    except:
        worked = False


    

    if worked:
        if not os.path.exists(jsonfile):
            my_logger.info("hackerdoor: access list was empty; New access list installed")
            shutil.move(tempfile,jsonfile)

        elif ( not( filecmp.cmp(tempfile,jsonfile))):
            # The files differ.
            print "Differ..."
            stamp = datetime.datetime.now().strftime("_%Y-%m-%d-%H:%M:%S");
            print stamp;
            oldfname = jsonfile + stamp;
            shutil.move(jsonfile,oldfname)
            shutil.move(tempfile,jsonfile)
            my_logger.info("hackerdoor: New access list installed")
        else:
            pass
            # The new download and the existing one are identical.  
            #  No action necessary.

    else:
        print "Failed!"


    
    
