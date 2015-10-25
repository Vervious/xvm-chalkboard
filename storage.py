"""
Handles persisting logs to a sql database,
in an append-only fashion using gauged, found on github,
which seems to be practical (unsure)
"""

from gauged import Gauged

gaugedStore = None


# ============ #
# WRITING DATA #
# ============ #

def write_chalkboardid_foruser(chalkboardID, sessionID, IP):
    """
    write the given IP and chalkboard identifier to the datastore,
    for the current time.
    """
    chalkboard_key = _chalkboard_key_for_id(chalkboardID)
    keyValueDict = {_ip_key_for_ip(IP): 1, chalkboard_key: 1}
    _write_keyvalues(keyValueDict)

def write_kerberos_foruser(kerberos, sessionID, IP):
    pass

def write_randomguess_foruser(randomguess, sessionID, IP):
    pass

def _write_keyvalues(keyvalues):
    """ 
    writes the given keyvalues to the (shared) datastore,
    for the current time.
    """
    _initialize_gaugestore_if_needed()
    print "hello"
    
    with gaugedStore.writer as writer:
        print "keyvalues: " + str(keyvalues)
        writer.add(keyvalues)


# ============ #
# READING DATA #
# ============ #

def read_total_counts_for_chalkboardid(chalkboardID):
    _initialize_gaugestore_if_needed()
    total = gaugedStore.aggregate(_chalkboard_key_for_id(chalkboardID), Gauged.SUM)
    return total


# ======= #
#  UTILS  #
# ======= #

def _chalkboard_key_for_id(chalkboardID):
    return "chalkboard_" + str(chalkboardID)

def _ip_key_for_ip(IP):
    return "ip_" + str(IP)

def _initialize_gaugestore_if_needed():
    global gaugedStore
    if gaugedStore is None:
        #print 'Initializing gauged store.'
        gaugedStore = Gauged('mysql://root@localhost/gauged_chalkboard')
        gaugedStore.sync() # initiate schema if necessary.
