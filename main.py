from flask import Flask, redirect, url_for, session, request
import storage
import json
import uuid
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello! Some coffee was spilled on another part of this website."

# dictionary of chalkboard id:description
# these will be relevant for the rest of the puzzle
STATA_CHALKBOARDS = {
    "xyz": "the main board"
}

# ========================== #
# DATA COLLECTION AND PUZZLE #
# ========================== #

# Entry point and entrypoint to second part of the puzzle
@app.route("/<chalkboardIdOrKerberos>/")
def parse_chalkboardOrKerberos(chalkboardIdOrKerberos):
    global STATA_CHALKBOARDS

    if chalkboardIdOrKerberos in STATA_CHALKBOARDS:
        return log_chalkboard(chalkboardIdOrKerberos)
    else:
        kerberosInfo = information_for_kerberos(chalkboardIdOrKerberos)
        if kerberosInfo is not None:
            return handle_kerberos(chalkboardIdOrKerberos)
    # we have a random guess
    return log_randomguess(chalkboardIdOrKerberos)

# Part 0
def log_chalkboard(chalkboardId):
    (sessionID, IPAddress) = id_and_ip_forcurrentsession()
    storage.write_chalkboardid_foruser(chalkboardId, sessionID, IPAddress)
    # begin the puzzle!
    return redirect(url_for('default_kerberos')) 

# Part 2
def handle_kerberos(kerberos):
    """ log the kerberos, to give us data on the chalkboard,
        and associate user id with MIT id (undergraduate, graduate, etc)
        assumes this is a valid kerberos """
    (sessionID, IPAddress) = id_and_ip_forcurrentsession()
    storage.write_kerberos_foruser(kerberos, sessionID, IPAddress)
    return "welcome to the puzzle"

def log_randomguess(randomGuess):
    (sessionID, IPAddress) = id_and_ip_forcurrentsession()
    storage.write_randomguess_foruser(randomGuess, sessionID, IPAddress)
    return "Trying to guess the url or something? GOOD LUCK! (or maybe your kerberos is just invalid)"

# Part 1
@app.route("/kerberos/")
def default_kerberos():
    # try to get people to replace the kerberos in the URL with their own
    return "look up! at the skys, the stars, and the url"


# ========== #
#  ANALYSIS  #
# ========== #

@app.route("/results/")
def results():
    return str(storage.read_total_counts_for_chalkboardid(1))


# =========== #
# ---UTILS--- #
# =========== #

def information_for_kerberos(kerberos):
    """ Find information for the given kerberos. 
        if kerberos non-existent, return None """
    r = requests.get("http://m.mit.edu/apis/people/" + str(kerberos))
    kerberosInfo = r.json()
    # see [http://m.mit.edu/docs/modules/people/api.html] for API doc
    if 'id' not in kerberosInfo:
        return None

    # we got here: it exists!
    return kerberos

def id_and_ip_forcurrentsession():
    """ Returns (sessionID, IP address) for the current session,
        generating a sessionID if it's the first time we've seen
        this user """
    SESSION_ID_KEY = 'sessionID'
    sessionID = None
    if SESSION_ID_KEY in session:
        sessionID = session[SESSION_ID_KEY]
    else:
        sessionID = str(uuid.uuid4())
    IPAddress = request.remote_addr
    return (sessionID, IPAddress)


# ============ #
# CONFIG LOGIC #
# ============ #

CONFIG_FILEPATH = './config.json'
try:
    configString = open(CONFIG_FILEPATH).read()
except:
    sys.exit('Could not load ' + CONFIG_FILEPATH + ' file')
configDict = json.loads(configString)
if "secret-key" not in configDict:
    sys.exit('Could not load \'secret-key\' from config file')

# set secret key for session tracking
app.secret_key = configDict["secret-key"]


if __name__ == "__main__":
    # for debugging only
    app.debug = True
    app.run(host='0.0.0.0')
