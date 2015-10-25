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

KEY_ALL_CHALKBOARDS = "chalkboard_all"

# for now, we'll just write lots of composite keys. In the future
# it may be worth looking into extending gauged with this functionality.
# The timeseries backend may not be the best... choice either, but let's roll with 
# it and see what happens.

def write_chalkboardid_foruser(chalkboardID, sessionID, IP, firstHit = False):
    """
    write the given IP and chalkboard identifier to the datastore,
    for the current time.
    Also write other useful analytics.
    """
    print "firstHit: " + str(firstHit)
    keyValueDict = {
        # collect data for an IP
        _ip_key_for_ip(IP): 1, 
        # enable sum over hits for each session
        _session_key_for_session(sessionID): 1,
        # enable sum over hits per chalkboard
        _chalkboard_key_for_id(chalkboardID): 1,
        # enable sum over first hits per chalkboard
        _chalkboard_firsthit_key_for_id(chalkboardID): int(firstHit),
        # enable sum over all chalkboards
        KEY_ALL_CHALKBOARDS: 1
    }
    _write_keyvalues(keyValueDict)

def write_kerberos_foruser(kerberos, sessionID, IP):
    keyValueDict = {
        # collect data for an IP
        _ip_key_for_ip(IP): 1, 
        # enable sum over hits for each session
        _session_key_for_session(sessionID): 1,
        # log the association for this kerberos and session, for future analytics
        _key_for_kerberos_and_session(kerberos, sessionID): 1
    }
    _write_keyvalues(keyValueDict)

def write_randomguess_foruser(randomguess, sessionID, IP):
    keyValueDict = {
        # collect data for an IP
        _ip_key_for_ip(IP): 1, 
        # enable sum over hits for each session
        _session_key_for_session(sessionID): 1,
        # log the association for this kerberos and session, for future analytics
        _key_for_session_and_allguesses(sessionID): 1,
        _key_for_session_and_guess(sessionID, randomguess): 1,
    }
    _write_keyvalues(keyValueDict)

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

def read_unique_total_counts_for_chalkboardid(chalkboardID):
    _initialize_gaugestore_if_needed()
    total = gaugedStore.aggregate(_chalkboard_firsthit_key_for_id(chalkboardID), Gauged.SUM)
    return total


# ======= #
#  UTILS  #
# ======= #

def _chalkboard_key_for_id(chalkboardID):
    return "chalkboard_" + str(chalkboardID)

def _chalkboard_firsthit_key_for_id(chalkboardID):
    return "chalkboard_firsthit_" + str(chalkboardID)

def _ip_key_for_ip(IP):
    return "ip_" + str(IP)

def _session_key_for_session(sessionID):
    return "session_" + str(sessionID)

def _key_for_kerberos_and_session(kerberos, session):
    return "kerberos_session_" + str(kerberos) + "_" + str(session)

def _key_for_session_and_allguesses(sessionID):
    return "session_allguesses_" + str(sessionID)

def _key_for_session_and_guess(sessionId, randomguess):
    return "session_guess_" + str(sessionId) + "_" + str(randomguess)

def _initialize_gaugestore_if_needed():
    global gaugedStore
    if gaugedStore is None:
        #print 'Initializing gauged store.'
        gaugedStore = Gauged('mysql://root@localhost/gauged_chalkboard')
        gaugedStore.sync() # initiate schema if necessary.
