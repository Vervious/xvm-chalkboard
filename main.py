import configerator
from flask import Flask, redirect, url_for, session, request
import storage
import uuid
import requests
import mpld3
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello! Some coffee was spilled on another part of this website. Deploy test #todo"

# dictionary of chalkboard id:description
# these will be relevant for the rest of the puzzle
STATA_CHALKBOARDS = {
    # choice of terms probably obscure enough that people will be attracted to
    # all equally, but relevant enough to be interesting (as opposed to random characters)
    "kafka": "the main board",
    "dickens": "the board to the right of the table area",
    "flaubert": "the board to the left of the table area",
    "vonnegut": "the big board",
    "kerouac": "board in front of 123",
    "bradbury": "board in front of blue thing",
    "brautigan": "board near the mirror",
    "murakami": "board near the restrooms"
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
    (sessionID, IPAddress, isFirstHit) = id_and_ip_forcurrentsession()
    storage.write_chalkboardid_foruser(chalkboardId, sessionID, IPAddress, firstHit=isFirstHit)
    # begin the puzzle!
    return redirect(url_for('default_kerberos'))


# Part 2
def handle_kerberos(kerberos):
    """ log the kerberos, to give us data on the chalkboard,
        and associate user id with MIT id (undergraduate, graduate, etc)
        assumes this is a valid kerberos """
    (sessionID, IPAddress, isFirstHit) = id_and_ip_forcurrentsession()
    storage.write_kerberos_foruser(kerberos, sessionID, IPAddress)
    return "Part 2. welcome to the puzzle"


def log_randomguess(randomGuess):
    (sessionID, IPAddress, isFirstHit) = id_and_ip_forcurrentsession()
    storage.write_randomguess_foruser(randomGuess, sessionID, IPAddress)
    return "Trying to guess the url or something? GOOD LUCK! (or maybe your kerberos is just invalid)"


# Part 1
@app.route("/kerberos/")
def default_kerberos():
    # try to get people to replace the kerberos in the URL with their own
    return "Ah. You found a puzzle. look up! at the skys, the stars, and the url."


# ========== #
#  ANALYSIS  #
# ========== #

@app.route("/results/")
def results():
    fig, ax = plt.subplots()

    resultString = "<br/><br/>"
    for chalkboardId in STATA_CHALKBOARDS:
        resultString += str(chalkboardId) + "<br/>"
        resultString += str(STATA_CHALKBOARDS[chalkboardId]) + "<br/>"
        resultString += str(storage.read_unique_total_counts_for_chalkboardid(chalkboardId))
        resultString += "<br/><hr/><br/><br/>"

        resultsSeries = storage.read_lastday_timeseries_for_chalkboardid(chalkboardId)
        ax.plot(resultsSeries.dates, resultsSeries.values, label=str(chalkboardId))

    ax.legend(loc=2)
    graphHTML = mpld3.fig_to_html(fig)
    resultString = graphHTML + "<br/>hits in the last 12 hours<br/>" + resultString
    return resultString


@app.route("/results/<chalkboardId>/")
def unique_results_for_chalkboard(chalkboardId):
    if chalkboardId not in STATA_CHALKBOARDS:
        return "chalkboard does not exist"
    return str(storage.read_unique_total_counts_for_chalkboardid(chalkboardId))


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
    """ Returns (sessionID, IP address, isFirstHit) for the current session,
        generating a sessionID if it's the first time we've seen
        this user """
    SESSION_ID_KEY = 'sessionID'
    sessionID = None
    isFirstHit = False
    if SESSION_ID_KEY in session:
        sessionID = session[SESSION_ID_KEY]
    else:
        sessionID = str(uuid.uuid4())
        session[SESSION_ID_KEY] = sessionID
        isFirstHit = True
    IPAddress = request.remote_addr
    return (sessionID, IPAddress, isFirstHit)


# ====== #
# CONFIG #
# ====== #

app.secret_key = configerator.SECRET_KEY


if __name__ == "__main__":
    # for debugging only
    app.debug = True
    app.run(host='0.0.0.0')
