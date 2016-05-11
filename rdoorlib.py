
# vim:ft=python:ai:expandtab:ts=4:



class GHCard:
    # This is the attribute byte, but only item defined is bit 0 == 1 is access allowed, 0 is denied
    access = None
    # facility code (FC)
    facility = None
    # card code (CC)
    card = None

    # if new ACL list says we are denied
    set_denied = False
    # if new ACL list says we are allowed
    set_allowed = False
    # if matches new ACL list entry
    no_change = False
    # if processed in new ACL list
    done = False

    def __init__( self, access, facilityCode, cardCode ):
        self.access = access
        self.fc = facilityCode
        self.cc = cardCode

class GHACL:
    acl = None

    def __init__( self, acl=None ):
        if acl is None:
            acl = []
        self.acl = acl

    def add( card ):
        self.acl.append( card )

    def deltaListTo( gold ):
        for card in gold.acl
        
