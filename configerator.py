import json
import sys

# ============ #
# CONFIG LOGIC #
# ============ #

CONFIG_FILEPATH = './config.json'
try:
    configString = open(CONFIG_FILEPATH).read()
except:
    sys.exit('Could not load ' + CONFIG_FILEPATH + ' file')
configDict = json.loads(configString)
if 'secret-key' not in configDict:
    sys.exit('Could not load \'secret-key\' from config file')
if 'mysql-store' not in configDict:
    sys.exit('Could not load database info from config file')

# set secret key for session tracking
# also allowed to use this for other purposes
SECRET_KEY = str(configDict['secret-key'])
MYSQL_STORE_STRING = str(configDict['mysql-store'])
