
# vim:ft=python:ai:expandtab:ts=4:

import socket
import re
import time
import select

class GHMUX:
    port = 23200
    server ='localhost'
    mux = None
    # re strings to build up patterns from
    #   matching the third (release) version of HSDC-0.1.0.5.ino
    #
    # from readACL()
    res_acl_header = re.escape(r'Record #, Address, Addribute, Card #,  in HEX format ') + r'\r*\n'
    # from printACLR()
    res_acl_data = r'"(?P<index>[A-F0-9]{2})", "(?P<addr>[A-F0-9]{4})", "(?P<attribute>[A-F0-9]{2})", "(?P<card_num>(?P<facility_code>[A-F0-9]{2})(?P<card_code>[A-F0-9]{4}))"\r*\n'
    res_acl = res_acl_header + res_acl_data
    # from printAllAclRecords()
    res_list_header_a = r'(?:[ ]\r*\n){2} Start printing of ACL List \r*\n \r*\n'
    res_list_header_b = re.escape(r' Format in Hex = Record #, EEProm Address, Attribute, Card code  ')
    res_list_header = res_list_header_a + res_list_header_b + r'\r*\n[ ]\r*\n'
    res_list_footer = r'[ ]\r*\n End printing of ACL List \r*\n'
    res_list = res_list_header + r'(?P<acl_list>(?:' + res_acl + r')*)' + res_list_footer
    # from aclAtt()
    res_att_header = r'Set Attribute of Record \d+ at address \d+\r*\n'
    res_att = res_att_header + res_acl
    # from eeMemory()
    res_byte = r'(?P<byte>[A-F0-9]{2}) '
    res_memory_header = r'Address (?P<address>[A-F0-9]{1,}) -HEX- '
    res_memory = res_memory_header + r'(?P<byte_list>(?:' + res_byte + r')*) \r*\n'

    # re to match the various command return values
    letter_re = {}
    letter_re['k'] = re.compile(res_acl)
    letter_re['j'] = letter_re['k']
    letter_re['v'] = letter_re['k']
    letter_re['o'] = re.compile(res_memory)
    letter_re['q'] = re.compile(res_att)
    letter_re['s'] = re.compile(res_list)

    def __init__(self, port=None, server=None):
        if port is not None:
            self.port = port
        if server is not None:
            self.server = server

    def connect(self):
        server_address = (self.server, self.port)
        self.mux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this should be connecting to localhost, so aggressive timeout
        self.mux.settimeout(1.0)
        self.mux.connect(server_address)

    def close(self):
        self.mux.shutdown(socket.SHUT_RDWR)
        self.mux.close()

    def run(self, wait=0.1, letter='k', options='00', cycle=3, timeout=0.1):
        self.connect()
        # set a (normally smaller) timeout for all the send/recv we will do
        self.mux.settimeout(timeout)
        # format for command is (A###) where ### is a options string
        # based on what letter command is being used
        command = '(' + letter + options + ')'
        command = command.upper()
        self.mux.send(command.encode())
        result = ''
        for count in range(cycle):
            rlist, _, _ = select.select([self.mux], [], [], 0.1)
            if rlist:
                # do what if recv raises a timeout, catch it?, not?
                recieved = self.mux.recv(2048)
                result += recieved.decode()
            # NOTE: we are explicitly not caring about any trailing stuff
            #   it might be garbage or the output from the next whatever
            #   all the letter_re should be designed to match (start anchored)
            #   open ended regular expressions
            matched = self.letter_re[letter].match(result)
            if matched:
                self.close()
                return matched
            time.sleep(wait)
        self.close()
        return None

    def add(self, attribute, facility_code, card_code):
        pass
        # call run(letter='v', options= attribute+facility_code+card_code

    def read_address(self, addr):
        address = str(addr)
        if not re.match(r'\A[0-9a-fA-F]{4}\Z', address):
            raise(Exception("read_address() address is not a 4 digit hexadecimal string"))
        match = self.run(letter='o', options=address)
        byte_list = match.group('byte_list')
        out = []
        for byte in re.finditer(self.res_byte, byte_list):
            out.append( byte.group('byte') )
        return out

    def acl_list(self):
        match = self.run(letter='s', options='', wait=0.5, cycle=30)
        acls = match.group('acl_list')
        out = []
        for acl in re.finditer(self.res_acl, acls):
            out.append({
                'index': acl.group('index'),
                'addr': acl.group('addr'),
                'attribute': acl.group('attribute'),
                'facility_code': acl.group('facility_code'),
                'card_code': acl.group('card_code'),
                'card_num': acl.group('card_num'),
                })
        # parts of card_num:
        #   facility_code
        #   card_code
        return out

class GHCard:
    # This is the attribute byte, but only item defined is bit 0 == 1 is access allowed, 0 is denied
    attribute = '00'    # 2 digit hex number as string
    allowed = False # this is boolean from bit 0 of attribute
    # facility code (FC) 2 digit hex number as string
    fc = None
    # card code (CC) 4 digit hex number as string
    cc = None

    # location in memory on the nano
    loc = None
    # index of ACL in memory on the nano
    index = None

    # name so we can log better, not stored on Arduino
    name = ''

    # if new ACL list says we are denied
    set_denied = False
    # if new ACL list says we are allowed
    set_allowed = False
    # if matches new ACL list entry
    no_change = False
    # if processed in new ACL list
    done = False

    def __init__( self, facilityCode, cardCode, location=None, allowed=None,
        attribute=None, name=None, index = None ):
        if index is not None:
            if re.match(r'\A[0-9a-fA-F]{2}\Z', str(index)):
                self.index = index.upper()
            else:
                raise(Exception("attribute was not a two character hexadecimal string"))
            self.attribute = attribute
        if name is not None:
            # TODO strip name down to 'safe' characters set for clean logging?
            #   e.g. [a-zA-Z0-9 ._'-]
            # this is silly, but I don't want newlines (for example) to end up in log lines
            self.name = name
        if attribute is not None:
            if re.match(r'\A[0-9a-fA-F]{2}\Z', str(attribute)):
                self.attribute = attribute.upper()
            else:
                raise(Exception("attribute was not a two character hexadecimal string"))
            self.attribute = attribute
        if re.match(r'\A[0-9a-fA-F]{2}\Z', str(facilityCode)):
            self.fc = facilityCode.upper()
        else:
            raise(Exception("facilityCode was not a two character hexadecimal string"))
        if re.match(r'\A[0-9a-fA-F]{4}\Z', str(cardCode)):
            self.cc = cardCode.upper()
        else:
            raise(Exception("cardCode was not a four character hexadecimal string"))
        self.loc = location
        self.allowed = False
        if allowed is not None:
            if self.allowed:
                self.allowed = True
                self.attribute = '01'; # this will need to change if we define more bits in attribute

    def __eq__( self, other ):
        if type(self) is type(other):
            return self.fc == other.fc and self.cc == other.cc
        else:
            return False

    def __hash__( self ):
        return hash((self.fc,self.cc))

class GHACL:
    acl = None
    # start location fo the ACL list on nan0
    start = None
    # end location of the ACL list on nano
    #   XXX verify this, but I think this is the first address not used by 
    #   the ACL list (e.i. pointer just after the last record)
    end = None

    def __init__( self, acl=None ):
        if acl is None:
            acl = []
        self.acl = acl

    def add( self,  card ):
        self.acl.append( card )

    def delta_list_to( self, gold ):
        s_card = {k:k for k in self.acl}
        seen = {}
        add = []
        to_deny = []
        to_allow = []

        for new in gold.acl:
            if new in seen:
                pass # WTF? duplicate new card data in gold? XXX
            seen[new] = 1
            new_card = True
            if new in s_card:
                old = s_card[new]
                new_card = False
                if new.allowed != old.allowed:
                    if new.allowed:
                        old.set_allowed = True
                        to_allow = old.loc
                    else:
                        old.set_denied = True
                        to_deny = old.loc
                old.done = True
            else:
                # not neccessarily will it have allowed set
                # we also keep track of cards that may not get in
                add.append(new)
            new.done = True
        for old in self.acl:
            if old.done:
                continue
            if old.allowed:
                # no card matched in new ACL list, disable it
                to_deny = old.loc
                old.set_denied = True
        if not to_allow and not to_deny and not add:
            # no changes are needed
            return None
        ## loop on to_allow for set attribute.0 = 1
        ## loop on to_deny for set attribute.0 = 0
        # how to figure out what the spare record spaces at the end are?
        # find the new record spots at the end for the add list to get locations from
        ## loop on add list to create calls for adding them
        ## add set acl_end if we need more space
            ## add spaceholder values for the last bit of the ACL list if we add extra allocations at the end

        ## loop and run all the calls to the nano
