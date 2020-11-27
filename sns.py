# This is *very* rough rn
import mysql.connector as connector
from mysql.connector import errorcode
from firebase import firebase
import json


'''Return a json file'''
def retrieve_file(file_path):

    with open(file_path) as f:
        file  = json.load(f)

    return file


'''Return a mysqlDB connection'''
def get_mysqlDB_connection(config):

    dbCon = None

    try:
        dbCon = connector.connect(
        user = config.get("mysqlUser"),
        password = config.get("mysqlPass"),
        host = config.get("mysqlHost"),
        database = config.get("mysqlDB"))
    except connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Wrong user or password!")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Bad Database!")
        else:
            print(err)

    return dbCon

'''Return an FB connection using provided json config'''
def get_fb_connection(config):
    return firebase.FirebaseApplication(config.get("databaseURL"), None)

'''Return a simple query request using provided json settings'''
def get_query(settings):

    queryString = "SELECT"
    for attribute in settings.get("attributes"):
        queryString = queryString + " " + attribute + ","

    queryString = queryString[:-1] + " FROM " + settings.get("attributeTable") + ";"

    return (queryString)

'''Establish the pipe between GB server and automatically forward to FB'''
def main():

    # Remove .TEMPLATE from crednetials.json.TEMPLATE and populate as necessary
    CREDENTIALS_FILE_PATH = "credentials.json"

    SETTINGS_FILE_PATH = "settings.json"

    config = retrieve_file(CREDENTIALS_FILE_PATH)
    settings = retrieve_file(SETTINGS_FILE_PATH)

    fb = get_fb_connection(config)
    db = get_mysqlDB_connection(config)

    cursor = db.cursor()
    query = get_query(settings)
    
    print(query)
    print(cursor.execute(get_query(settings)))

if __name__ == "__main__":
    main()
