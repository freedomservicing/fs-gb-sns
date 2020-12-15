"""Backend pipe for GB -> FB

:author: Caden Koscinski
:author: Noah Martino
:see: settings.json.TEMPLATE
:see: credentials.json.TEMPLATE
"""

import firebase_admin
from firebase_admin import credentials, firestore
import mysql.connector as connector
from mysql.connector import errorcode
import os
import json


"""Manage a specified file"""
class file_manager:

    __file_path = None


    """Constructor
    :param file_path: absolute or relative file path
    """
    def __init__(self, file_path):
        self.__file_path = file_path


    """Read the specified file
    :returns: dict of json-formatted file
    """
    def read_json(self):
        with open(self.__file_path) as f:
            file = json.load(f)
        return file


"""Pipe connecting and facilitating the transfer of data between the GB mysql DB
and the CaaS FS DB"""
class gb_pipe:

    __credentials = None
    __settings = None
    __mysqlDB = None
    __fsDB = None

    # Will be set to false during construction if a connection to either DB fails
    __functional = True


    """Constructor
    :param credentials: valid credentials JSON object
    :param settings: valid settings JSON object
    """
    def __init__(self, credentials, settings):
        self.__credentials = credentials
        self.__settings = settings
        self.__init_mysqlDB()
        self.__init_fsDB()


    """Establish a connection to the GB DB
    :see: credentials.json
    """
    def __init_mysqlDB(self):
        try:
            self.__mysqlDB = connector.connect(
            user = self.__credentials.get("mysqlUser"),
            password = self.__credentials.get("mysqlPass"),
            host = self.__credentials.get("mysqlHost"),
            database = self.__credentials.get("mysqlDB"))
        except connector.Error as err:
            self.__functional = False
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Wrong user or password!")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Bad Database!")
            else:
                print(err)


    """Establish a connection to the FS DB
    :see: credentials.json/googleAuthPath
    :see: settings.json/firestoreAddress
    """
    def __init_fsDB(self):
        try:
            auth_path = self.__credentials["googleAuthPath"]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = auth_path
            self.__fsDB = firestore.Client(project=self.__settings["firestoreAddress"])
        except:
            self.__functional == False


    """Compile a query based upon predefined attributes and a target table
    :see: settings.json/attributeTable
    :see: settings.json/attributes
    :returns: formatted mysql search query
    """
    def __get_query(self, query_name):
        queryString = "SELECT"
        for attribute in self.__settings["queries"][query_name]["attributes"]:
            queryString = queryString + " " + attribute + ","
        queryString = queryString[:-1] + " FROM " + self.__settings["queries"][query_name]["attributeTable"]
        return queryString


    """Execute a query search on the mysql DB
    :param query: valid mysql query
    :returns: list of observations
    """
    def __submit_query(self, query):
        cursor = self.__mysqlDB.cursor()
        cursor.execute(query)
        mysql_data = []
        for observation in cursor:
            mysql_data.append(observation)
        return mysql_data


    """Reformat a basic list of mysql observations into a dict including the columns
    :param mysql_observations: list of all observations pulled from the preconfigured
    query
    :see: settings.json/attributes
    :returns: dict form of all observations
    """
    def __restructure_query_response(self, query_name, mysql_observations):
        attributes = self.__settings["queries"][query_name]["attributes"]
        mysql_bound_data = []
        for observation in mysql_observations:
            attributes_index = 0
            obs_dict = {}
            for element in observation:
                obs_dict[attributes[attributes_index]] = element
                attributes_index += 1
            mysql_bound_data.append(obs_dict)
        return mysql_bound_data


    """Pipe data from the GB backend and format based upon preconfigured parameters
    :see: settings.json
    :returns: formatted JSON with keys binding mysql values
    """
    def get_formatted_query(self, query_name):

        # TODO: Remove Hard-Coded Query
        return self.__restructure_query_response(query_name, self.__submit_query(self.__get_query(query_name)))


    """Return the status of the pipe - True if both GB and FS connections are live
    :returns: pipe status
    """
    def is_functional(self):
        return self.__functional


    """Convert data into a format suitable for FS submission
    :param mysql_observation: formatted mysql_observation from an entry generated
    by self.__restructure_query_response()
    :see: settings.json/relationships
    :returns: restructured json aligned with FS structure
    """
    def __sanitize_data(self, mysql_observation):

        relationships = self.__settings["relationships"]
        transaction_data = {}

        for key in relationships:

            relationship = relationships[key]
            assoc_key = relationship[0]

            # Only add data that is mapped in settings
            if assoc_key is not None:
                if assoc_key in mysql_observation:

                    raw_value = mysql_observation[relationship[0]]

                    mysql_value = raw_value

                    type_id = relationship[1]
                    if type_id == "string":
                        mysql_value = str(raw_value)
                    elif type_id == "double":
                        mysql_value = float(raw_value)
                    elif type_id == "integer":
                        mysql_value = int(raw_value)
                    # else:
                    #     print("No type identified: Defaulting to raw input")

                    transaction_data[key] = mysql_value

        return transaction_data


    """Prepare a JSON for FS submission by invoking sanitation methods
    :param mysql_observations: formatted mysql query - generated from
    self.__restructure_query_response()
    :returns: sanitized JSON
    """
    def __prepare_fs_submission(self, mysql_observations):
        prepped_data = []
        for observation in mysql_observations:
            prepped_data.append(self.__sanitize_data(observation))
        return prepped_data


    """Retrieve a JSON suitable for FS submission
    :returns: FS compatible JSON based upon preconfigured relationships
    :see: settings.json/relationships
    """
    def get_fs_submission(self, query_name):
        return self.__prepare_fs_submission(self.get_formatted_query(query_name))


    """Commit data to the FS

    DO NOT INVOKE OR OTHERWISE CALL - THIS IS A PROTOTYPE / PSUEDOCODE FUNCTION
    """
    def commit_data(self, data):

        collection = self.__fsDB.collection("Machines")

        for entry in data:

            # TODO - Assign UUID to all GB Machines and assign appropriately
            data["machine_id"] = "PLACEHOLDER_UUID_A"

            machine_document = collection.document(data["machine_id"])
            machine_activity = machine_document.collection("Activity")

            # TODO - Assign UUID to all unique Transactions and assign appropriately
            transaction_document = machine_activity.document("PLACEHOLDER_UUID_B")

            # TODO - Figure out if this actually works (???)
            data.pop("machine_id", None)

            transaction_document.set(data)


"""Manages and encapsulates the GB pipe"""
class pipe_manager():

    __credentials_file_path = None
    __settings_file_path = None
    __pipe = None


    # Constructor
    def __init__(self, credentials_file_path, settings_file_path):
        self.__credentials_file_path = credentials_file_path
        self.__settings_file_path = settings_file_path
        self.__pipe = self.__build_pipe()


    """Build a pipe using the predefined configuration parameters
    :returns: gb_pipe object
    """
    def __build_pipe(self):

        credentials_manager = file_manager(self.__credentials_file_path)
        credentials_file = credentials_manager.read_json()

        settings_manager = file_manager(self.__settings_file_path)
        settings_file = settings_manager.read_json()

        return gb_pipe(credentials_file, settings_file)


    """Return the pipe assigned to the manager
    :returns: assigned pipe - will be None if the pipe is broken
    """
    def get_pipe(self):
        return self.__pipe


"""Establish an active listener and pipe between the GB backend and CaaS-FS frontend

Connection to the FS requires access to a user's Google API service key.
Under credentials.json, populate the googleAuthPath field with the absolute path
to your Google API service key JSON.
"""
def main():

    # Remove .TEMPLATE from credentials.json.TEMPLATE and populate as necessary
    CREDENTIALS_FILE_PATH = "credentials.json"
    SETTINGS_FILE_PATH = "settings.json"

    gb_pipe_manager = pipe_manager(CREDENTIALS_FILE_PATH, SETTINGS_FILE_PATH)

    if gb_pipe_manager.get_pipe().is_functional:
        # TODO: Implement listener and regulate data submissions

        # Temporary code to verify functionality

        # Hard-Coded Request
        query_name = "transactions"

        data = gb_pipe_manager.get_pipe().get_fs_submission(query_name)
        data_index = 0
        max_index = 4
        while (data_index <= max_index):
            print("\n", data[data_index])
            data_index += 1

    else:
        print("Unable to establish pipe manager. Check configuration and try again.")


# Main execution
if __name__ == "__main__":
    main()
