import socket
import sys
import os
import json
from pprint import pprint



door_user = "hackerdoor"

rootdir = '/home/{0}'.format(door_user)

uds_address = '{0}/doorsock'.format(rootdir);

json_dir = '{0}/json'.format(rootdir);



def read_acl():
    for version in [0]:
        json_file = '{0}/access.json'.format(json_dir)
        json_data=open(json_file)
        data = json.load(json_data)
        json_data.close()
        pprint(data)







def start_listening_uds():

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
                    response = "Sure, why not"
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(response)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
            
        finally:
            # Clean up the connection
            connection.close()



def knock_uds(message='0303030303'):

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
