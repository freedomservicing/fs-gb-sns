"""Backend pipe for GB -> FB

:author: Caden Koscinski
:author: Noah Martino
:see: https://docs.google.com/document/d/1CmbGNYDnQZ6idU0OOlEq3P8plQmYn6p8NcZcOXrTZAw/edit
:see: settings.json.TEMPLATE
:see: credentials.json.TEMPLATE
"""

import firebase_admin
from firebase_admin import credentials, firestore
import argparse
import mysql.connector as connector
from mysql.connector import errorcode
from id_manager import id_manager
from file_manager import file_manager
from listener import listener_manager
import os
import json


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

    If entries is left as default, the entire db will be queries
    """
    def __submit_query(self, query, entries=-1):
        cursor = self.__mysqlDB.cursor()
        cursor.execute(query)
        mysql_data = []
        if entries == -1:
            for observation in cursor:
                mysql_data.append(observation)
        else:
            while entries > 0:
                mysql_data.append(cursor.fetchone())
                entries -= 1
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
    def __sanitize_data(self, mysql_observation, relationships=None):

        data = {}

        for key in mysql_observation:

            key_value = mysql_observation[key]
            if key_value == 0:
                key_value = "0"
            else:
                key_value = str(key_value)

            if relationships != None:
                if key in relationships:
                    key = relationships[key]

            data[str(key)] = key_value

        return data


    """Prepare a JSON for FS submission by invoking sanitation methods
    :param mysql_observations: formatted mysql query - generated from
    self.__restructure_query_response()
    :returns: sanitized JSON
    """
    def __prepare_fs_submission(self, mysql_observations, query_name):
        prepped_data = []

        for observation in mysql_observations:
            prepped_data.append(self.__sanitize_data(observation, self.__settings["queries"][query_name]["relationships"]))

        return prepped_data


    """Retrieve a JSON suitable for FS submission
    :returns: FS compatible JSON based upon preconfigured relationships
    :see: settings.json/relationships
    """
    def get_fs_submission(self, query_name):
        return self.__prepare_fs_submission(self.get_formatted_query(query_name), query_name)


    """Commit data to the FS

    DO NOT INVOKE OR OTHERWISE CALL - THIS IS A PROTOTYPE / PSUEDOCODE FUNCTION
    """
    def commit_data(self, data, endpoint, id_manager, meta_json):

        current_collection = self.__fsDB.collection(endpoint)

        for entry in data:

            # print("\nAdding Transaction:\n", entry, "\nUsing ID: ", id_manager.issue_id(entry, meta_json))

            current_document = current_collection.document(id_manager.issue_id(entry, meta_json))
            current_document.set(entry)


    """Mock WIP Method for Listener

    EXCERCISE CAUTION WHEN CALLING
    """
    def commit_listener_data(self, data, meta_path):

        # collection = self.__fsDB.collection(SOMETHING FROM META_PATH)

        pass


"""Manages and encapsulates the GB pipe"""
class pipe_manager:

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


"""Execute first run procedure

ONLY TO BE INSTANCED FROM MAIN OF SNS
"""
class first_run_operator:

    __query_name = None
    __meta = None

    def __init__(self, query_name, meta=False):
        self.__query_name = query_name
        self.__meta = meta
        self.__initial_draw()

    def __initial_draw(self):

        # Remove .TEMPLATE from credentials.json.TEMPLATE and populate as necessary
        CREDENTIALS_FILE_PATH = "credentials.json"
        SETTINGS_FILE_PATH = "settings.json"
        ID_CACHE_PATH = "transaction_id_cache.json"

        gb_pipe_manager = pipe_manager(CREDENTIALS_FILE_PATH, SETTINGS_FILE_PATH)
        idm_instance = id_manager(ID_CACHE_PATH, SETTINGS_FILE_PATH)

        settings_manager = file_manager(SETTINGS_FILE_PATH)
        settings_json = settings_manager.read_json()

        if gb_pipe_manager.get_pipe().is_functional():

            reformatted_terminal_id = None

            if self.__query_name == "transactions":
                # TEST AREA: Retrieve Terminal Info
                q_name = "terminal_information"
                tdata = gb_pipe_manager.get_pipe().get_fs_submission(q_name)
                for entry in tdata:
                    # print("\n", entry)
                    pass
                print("\n")

                reformatted_terminal_id = {}
                for entry in tdata:
                    simple_id = str(entry["simple_id"])
                    reformatted_terminal_id[simple_id] = str(entry["serial"])
                for entry in reformatted_terminal_id:
                    # print("\n", entry, reformatted_terminal_id[entry])
                    pass
                print("\n")
                # END

            data = gb_pipe_manager.get_pipe().get_fs_submission(self.__query_name)

            endpoint = settings_json["queries"][self.__query_name]["endpoint"]

            gb_pipe_manager.get_pipe().commit_data(data, endpoint, idm_instance, reformatted_terminal_id)

        else:
            print("Unable to establish pipe manager. Check configuration and try again.")


"""Execute listener procedure

ONLY TO BE INSTANCED FROM MAIN OF SNS
"""
class listener_operator:

    def __init__(self):
        self.__conduct_listening()

    def __conduct_listening(self):

        # Listener operation

        # TODO: Implement listener and regulate data submissions
        # reference_settings = file_manager(SETTINGS_FILE_PATH)
        # listener_managers = []
        # for query in reference_settings.read_json()["queries"]:
        #     connector = gb_pipe_manager.get_pipe()
        #     listener_managers.append(listener_manager(listener(connector, query)))

        pass


def flush_transaction_id_cache(path_to_cache="transaction_id_cache.json", path_to_template="transaction_id_cache.json.TEMPLATE"):
    print('Flushing transaction id cache')
    successful_flush = True
    try:
        cache_manager = file_manager(path_to_cache)
        template_manager = file_manager(path_to_template)
        cache_manager.write_json(template_manager.read_json())
    except:
        successful_flush = False
    return successful_flush


"""Establish an active listener and pipe between the GB backend and CaaS-FS frontend

Connection to the FS requires access to a user's Google API service key.
Under credentials.json, populate the googleAuthPath field with the absolute path
to your Google API service key JSON.
"""
def main():

    parser = argparse.ArgumentParser(description='Creates a listener for the FireStore')
    parser.add_argument('-f', '--flush', dest='flush_output', action='store_true', help='Flush the transaction id cache')
    args = parser.parse_args()
    if args.flush_output:
        flush_transaction_id_cache()

    SETTINGS_FILE_PATH = "settings.json"
    settings_manager = file_manager(SETTINGS_FILE_PATH)

    if settings_manager.is_functional():
        settings_json = settings_manager.read_json()
        for query in settings_json["queries"]:
            query_json = settings_json["queries"][query]
            if query_json["first_run"] and query != "terminal_information":
                fr_operator = first_run_operator(query)
                settings_json["queries"][query]["first_run"] = False
                settings_manager.write_json(settings_json)
                print("\nFirst Run Complete for Query:", query)
    

    print("\nCompleted First Run Procedures")

    # Procedes to Spool Listeners
    l_operator = listener_operator()

# Main execution
if __name__ == "__main__":
    main()
