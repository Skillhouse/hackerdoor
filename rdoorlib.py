
# vim:ft=python:ai:expandtab:ts=4:



class GHCard:
    # This is the attribute byte, but only item defined is bit 0 == 1 is access allowed, 0 is denied
    access = None
    allowed = False # this is boolean from bit 0 of access
    # facility code (FC)
    fc = None
    # card code (CC)
    cc = None

    # location in memory on the nano
    loc = None

    # if new ACL list says we are denied
    set_denied = False
    # if new ACL list says we are allowed
    set_allowed = False
    # if matches new ACL list entry
    no_change = False
    # if processed in new ACL list
    done = False

    def __init__( self, access, facilityCode, cardCode, location=None ):
        self.access = access
        self.fc = facilityCode
        self.cc = cardCode
        self.loc = location
        # XXX need logic here
        self.allowed = False

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

    def deltaListTo( self, gold ):
        s_card = {k:k for k in self.acl}
        seen = {}
        add = []
        denied = []
        allowed = []
        # n is new card
        for n in gold.acl:
            if n in seen:
                pass # WTF? duplicate new card data in gold? XXX
            seen[n] = 1
            new_card = True
            if n in s_card:
                o = s_card[n]
                new_card = False
                if n.allowed != o.allowed:
                    if n.allowed:
                        o.set_allowed = True
                        allowed = o.loc
                    else:
                        o.set_denied = True
                        denied = o.loc
                o.done = True
            else:
                # not neccessarily will it have allowed set
                # we also keep track of cards that may not get in
                add.append(n)
            n.done = True
        for o in self.acl:
            if o.done:
                continue
            if o.allowed:
                # no card matched in new ACL list, disable it
                denied = o.loc
                o.set_denied = True
        # how to figure out what the spare record spaces at the end are?
        # find the new record spots at the end for the add list to get locations from
        ## loop on allowed for set access.0 = 1
        ## loop on denied for set access.0 = 0
        ## loop on add list to create calls for adding them
        ## add set acl_end if we need more space
            ## add spaceholder values for the last bit of the ACL list if we add extra allocations at the end

        ## loop and run all the calls to the nano
