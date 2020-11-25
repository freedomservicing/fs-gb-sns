# This is *very* rough rn
import mysql.connector as connector
from mysql.connector import errorcode
from firebase import firebase
import json

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

'''Return an FB connection using provided json config'''
def firebase_connection(credentials_file_path):

    with open(credentials_file_path) as f:
        firebase_config  = json.load(f)

    return firebase.FirebaseApplication(firebase_config.get("databaseURL"), None)


'''Establish the pipe between GB server and automatically forward to FB'''
def main():

    # Remove .TEMPLATE from crednetials.json.TEMPLATE and populate as necessary
    CREDENTIALS_FILE_PATH = "credentials.json"

    fb = firebase_connection(CREDENTIALS_FILE_PATH)

    print("\nTesting Firebase Connection: \n", fb.get("Machines", None), "\n")


if __name__ == "__main__":
    main()
