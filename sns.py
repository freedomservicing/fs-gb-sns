# This is *very* rough rn
import mysql.connector as connector
from mysql.connector import errorcode
from firebase import firebase
# Fill In the blanks with the relevant info for your test DB or the live DB.
# In the future I will set this to be loaded from a text file.
try:
    dbCon = connector.connect(user = '', password = '', host = '', database = '')
except connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Wrong user or password!")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Bad Database!")
    else:
        print(err)

firebase_config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": ""
}

fb = firebase.FirebaseApplication(firebase_config.get("databaseURL"), None)

result = fb.get("Machines", None)

print(result)