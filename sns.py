## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

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
from listener import listener, listener_manager
import os
import json

piece_type_ref = {
"1": "emails",
"2": "docs",
"3": "personals",
"4": "cellphones",
# Fingerprints are currently not populated on the GB backend
"5": "fingerprints",
"6": "camera_images"
}

class identity_piece:

    def __init__(self, piece_obs, settings_json):

        self.__settings_json = settings_json

        self.__piece_obs = piece_obs
        self.__gb_piece_id = self.__identity_obs[settings_json["queries"]["identities"]["relationships"]["id"]]


class identity:

    def __init__(self, identity_obs, settings_json):

        self.__settings_json = settings_json

        self.__identity_obs = identity_obs
        self.__gb_identity_id = self.__identity_obs[settings_json["queries"]["identities"]["relationships"]["id"]]


class internal_identity_cache:

    # Constructor
    def __init__(self):

        self.__identities_cache = None
        self.__identity_notes_cache = None
        self.__identity_pieces_cache = None
        self.__identity_camera_images_cache = None
        self.__identity_cells_cache = None
        self.__identity_docs_cache = None
        self.__identity_emails_cache = None
        self.__identity_fingerprints_cache = None
        self.__identity_personal_cache = None

        self.__setter_dict = {
        "identities proper": self.set_id_cache,
        "notes": self.set_notes_cache,
        "pieces": self.set_pieces_cache,
        "camera images": self.set_camera_images_cache,
        "cells": self.set_cells_cache,
        "docs": self.set_docs_cache,
        "emails": self.set_emails_cache,
        "fingerprints": self.set_fingerprints_cache,
        "personal": self.set_personal_cache
        }

        self.__getter_dict = {
        "identities proper": self.get_id_cache,
        "notes": self.get_notes_cache,
        "pieces": self.get_pieces_cache,
        "camera images": self.get_camera_images_cache,
        "cells": self.get_cells_cache,
        "docs": self.get_docs_cache,
        "emails": self.get_emails_cache,
        "fingerprints": self.get_fingerprints_cache,
        "personal": self.get_personal_cache
        }

    # Umbrella Dicts

    def get_setters(self):
        return self.__setter_dict

    def get_getters(self):
        return self.__getter_dict

    # Setters

    def set_id_cache(self, cache):
        self.__identities_cache = cache

    def set_notes_cache(self, cache):
        self.__identity_notes_cache = cache

    def set_pieces_cache(self, cache):
        self.__identity_pieces_cache = cache

    def set_camera_images_cache(self, cache):
        self.__identity_camera_images_cache = cache

    def set_cells_cache(self, cache):
        self.__identity_cells_cache = cache

    def set_docs_cache(self, cache):
        self.__identity_docs_cache = cache

    def set_emails_cache(self, cache):
        self.__identity_emails_cache = cache

    def set_fingerprints_cache(self, cache):
        self.__identity_fingerprints_cache = cache

    def set_personal_cache(self, cache):
        self.__identity_personal_cache = cache

    # Getters

    def get_id_cache(self):
        return self.__identities_cache

    def get_notes_cache(self):
        return self.__identity_notes_cache

    def get_pieces_cache(self):
        return self.__identity_pieces_cache

    def get_camera_images_cache(self):
        return self.__identity_camera_images_cache

    def get_cells_cache(self):
        return self.__identity_cells_cache

    def get_docs_cache(self):
        return self.__identity_docs_cache

    def get_emails_cache(self):
        return self.__identity_emails_cache

    def get_fingerprints_cache(self):
        return self.__identity_fingerprints_cache

    def get_personal_cache(self):
        return self.__identity_personal_cache


# """Execute procedures concerning the merging and committing of identities
# """
# class identity_operator:
#
#     def __init__(self, pipe, meta_cache_path="meta_cache.json"):
#
#         self.__meta_cache_path = meta_cache_path
#
#         self.__pipe = pipe
#
#         self.__execute_merge_protocol()
#
#     def __execute_merge_protocol(self):
#
#         identities_proper = self.__internal_cache.get_getters()["identities proper"]()
#
#         identity_idm = id_manager("identities")
#
#     """Override meta for identities with our UID system
#
#     CHECK IF IDENTITY SERIALS NEED TO BE PRESERVED
#     """
#     def __associate_identity_uids(identity_observations, meta_cache_path):
#
#         identity_idm = id_manager("identities")
#
#         meta_cache_file = file_manager(meta_cache_path)
#         meta_cache_json = {}
#
#         # TODO: Correct procedure if fails to read
#         if meta_cache_file.is_functional():
#             meta_cache_json = meta_cache_file.read_json()
#
#         for identity in identity_observations:
#             current_identity = identity_observations[identity]
#             meta_cache_json[identity] = identity_idm.issue_id(current_identity)
#
#         meta_cache_file.write_json(meta_cache_json)


"""Pipe connecting and facilitating the transfer of data between the GB mysql DB
and the CaaS FS DB"""
class gb_pipe:

    __credentials = None
    __settings = None
    __mysqlDB = None
    __fsDB = None

    # Will be set to false during construction if a connection to either DB fails
    __functional = True

    # Debug for checking pagination
    __transactions_pushed = 0


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
                print("General Error:", err)


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
    def get_query(self, query_name):
        queryString = "SELECT"
        for attribute in self.__settings["queries"][query_name]["attributes"]:
            queryString = queryString + " " + attribute + ","
        queryString = queryString[:-1] + " FROM " + self.__settings["queries"][query_name]["attributeTable"]
        return queryString


    """Execute a query search on the mysql DB
    :param query: valid mysql query
    :returns: list of observations

    If entries is left as default, all observations from the query will be returned
    """
    def submit_query(self, query, entries=-1):
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
    def restructure_query_response(self, query_name, mysql_observations):
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
        return self.restructure_query_response(query_name, self.submit_query(self.get_query(query_name)))


    """Return the status of the pipe - True if both GB and FS connections are live
    :returns: pipe status
    """
    def is_functional(self):
        return self.__functional


    """Convert data into a format suitable for FS submission
    :param mysql_observation: formatted mysql_observation from an entry generated
    by self.restructure_query_response()
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
    self.restructure_query_response()
    :returns: sanitized JSON
    """
    def prepare_fs_submission(self, mysql_observations, query_name):
        prepped_data = []

        for observation in mysql_observations:
            prepped_data.append(self.__sanitize_data(observation, self.__settings["queries"][query_name]["relationships"]))

        return prepped_data


    """Retrieve a JSON suitable for FS submission
    :returns: FS compatible JSON based upon preconfigured relationships
    :see: settings.json/relationships
    """
    def get_fs_submission(self, query_name):
        return self.prepare_fs_submission(self.get_formatted_query(query_name), query_name)


    """Commit data to the FS
    """
    def commit_data(self, entry, endpoint, id):

        # current_collection = self.__fsDB.collection(endpoint)

        # print("\nAdding:\n", entry, "\nUsing ID: ", id)
        pass

        # current_document = current_collection.document(id)
        # current_document.set(entry)


"""Manages and encapsulates the GB pipe"""
class pipe_manager:

    # Constructor
    def __init__(self, credentials_file_path="credentials.json", settings_file_path="settings.json"):
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
    # __internal_cache = None

    # def __init__(self, query_name, meta=False, internal_cache=None):
    def __init__(self, query_name, meta=False):
        self.__query_name = query_name
        self.__meta = meta
        # self.__internal_cache = internal_cache
        self.__initial_draw()

    def __initial_draw(self):
        # Remove .TEMPLATE from credentials.json.TEMPLATE and populate as necessary
        CREDENTIALS_FILE_PATH = "credentials.json"
        SETTINGS_FILE_PATH = "settings.json"
        ID_CACHE_PATH = "generic_id_cache.json"
        if not self.__meta:
            self.flush_cache(self.__query_name, ID_CACHE_PATH)

        gb_pipe_manager = pipe_manager(CREDENTIALS_FILE_PATH, SETTINGS_FILE_PATH)

        settings_manager = file_manager(SETTINGS_FILE_PATH)
        settings_json = settings_manager.read_json()

        if gb_pipe_manager.get_pipe().is_functional():

            data = gb_pipe_manager.get_pipe().get_fs_submission(self.__query_name)

            # Update the meta cache if necessary
            query = settings_json["queries"][self.__query_name]
            if query["meta"]:
                # TEST AREA: Retrieve Terminal Info
                update_meta_cache(query, self.__query_name, gb_pipe_manager.get_pipe())
                # END
            elif query["exclusion"] == None:
                idm_instance = id_manager(self.__query_name, ID_CACHE_PATH, SETTINGS_FILE_PATH)
                self.__initialize_listener_cache(data[-1])
                endpoint = query["endpoint"]
                query_metadata = None
                obs_ref = None
                if query["meta_endpoint"] != None:
                    obs_ref = query["meta_endpoint"]
                    query_metadata = get_meta_for_query(self.__query_name)
                    print(query_metadata)

                for entry in data:

                    id = idm_instance.issue_id(entry, obs_ref, query_metadata)
                    gb_pipe_manager.get_pipe().commit_data(entry, endpoint, id)

            elif query["exclusion"] == "identity_head":
                idm_instance = id_manager(self.__query_name, ID_CACHE_PATH, SETTINGS_FILE_PATH)
                self.__initialize_listener_cache(data[-1])
                endpoint = query["endpoint"]
                query_metadata = None
                obs_ref = None
                if query["meta_endpoint"] != None:
                    obs_ref = query["meta_endpoint"]
                    query_metadata = get_meta_for_query(self.__query_name)
                    print(query_metadata)

                for entry in data:

                    id = idm_instance.issue_id(entry, obs_ref, query_metadata)
                    gb_pipe_manager.get_pipe().commit_data(entry, endpoint, id)

                    # Add the gb id for every identity
                    gb_simple_id = entry[query["relationships"]["id"]]

                    cache_file = idm_instance.get_id_cache_file()
                    cache_json = cache_file.read_json()
                    cache_json[self.__query_name].update({gb_simple_id : {}})
                    cache_file.write_json(cache_json)

                    idm_instance.update_cache_file_via_path(self.__query_name + '*' + gb_simple_id + '*' + "UID" + '*' +id, '*')

            elif query["exclusion"] == "identity pieces":

                specific_idms = {}

                for i in range(1, 6):
                    specific_idms.update({f"{i}" : id_manager("identity_" + piece_type_ref[f"{i}"], ID_CACHE_PATH, SETTINGS_FILE_PATH)})

                idm_instance = id_manager(self.__query_name, ID_CACHE_PATH, SETTINGS_FILE_PATH)
                self.__initialize_listener_cache(data[-1])
                query_metadata = None
                obs_ref = None
                if query["meta_endpoint"] != None:
                    obs_ref = query["meta_endpoint"]
                    query_metadata = get_meta_for_query(self.__query_name)
                    print(query_metadata)

                cache_file = idm_instance.get_id_cache_file()
                cache_json = cache_file.read_json()

                base_endpoint = query["endpoint"]

                for entry in data:

                    id = idm_instance.issue_id(entry, obs_ref, query_metadata)

                    piece_id = entry[query["relationships"]["id"]]
                    parent_identity_id = entry[query["relationships"]["identity_id"]]
                    parent_identity_uid = cache_json["identities"][parent_identity_id]["UID"]

                    # Check if the following returns a string or int
                    piece_type = entry[query["relationships"]["piecetype"]]

                    subquery_name = "identity_" + piece_type_ref[piece_type]

                    subquery = gb_pipe_manager.get_pipe().get_query(subquery_name)
                    subquery += " WHERE identityPiece_id=" + piece_id

                    # print("SQ:" + subquery)

                    current_pieces = gb_pipe_manager.get_pipe().restructure_query_response(subquery_name, gb_pipe_manager.get_pipe().submit_query(subquery))
                    sanitized_pieces = gb_pipe_manager.get_pipe().prepare_fs_submission(current_pieces, subquery_name)

                    for piece in sanitized_pieces:

                        inner_cache = "identities" + "*" + parent_identity_id + "*" + subquery_name + "*" + "last_" + subquery_name

                        print("IC:" + inner_cache)

                        id = specific_idms[piece_type].issue_id(entry, obs_ref, query_metadata, level_path=inner_cache)
                        # Map for subquery_name - Make more readable on FS
                        gb_pipe_manager.get_pipe().commit_data(entry, base_endpoint + parent_identity_uid + subquery_name, id)

            else:
                pass

        else:
            print("Unable to establish pipe manager. Check configuration and try again.")


    def __initialize_listener_cache(self, sanitized_obs_json, settings_file_path="settings.json", cache_path="listener_cache.json"):
        settings_manager = file_manager(settings_file_path)
        listener_cache_manager = file_manager(cache_path)
        if settings_manager.is_functional():
            query_json = settings_manager.read_json()["queries"][self.__query_name]
            listener_column = query_json["listener_column"]
            active_column = query_json["relationships"][listener_column]

            listener_cache_contents = listener_cache_manager.read_json() if listener_cache_manager.is_functional() else {}
            new_latest = {"listener_record" : { self.__query_name : {"last_id" : sanitized_obs_json[active_column]}}}
            listener_cache_contents.update(new_latest)
            listener_cache_manager.write_json(listener_cache_contents, cache_path)
        else:
            print("Query json is not functional.")


    def flush_cache(self, query_name=None, path_to_cache="generic_id_cache.json"):
        cache_manager = file_manager(path_to_cache)
        if query_name is not None:
            print(f'Flushing id cache for {query_name}')
            successful_flush = True
            try:
                cache_contents = cache_manager.read_json() if cache_manager.is_functional() else {}
                if query_name in cache_contents.keys():
                    del cache_contents[query_name]
                cache_manager.write_json(cache_contents)
                # template_manager = file_manager(path_to_template)
                # cache_manager.write_json(template_manager.read_json())

            except:
                successful_flush = False
            return successful_flush
        else:
            cache_manager.write_json({})

    # def get_internal_cache(self):
    #     return self.__internal_cache


"""Update/append to the meta_cache entry for a given query
:returns: A dictionary of the contents of the meta_cache for the given query.
"""
def update_meta_cache(query_dict, query_name, pipe, cache_path="meta_cache.json"):
    meta_cache_manager = file_manager(cache_path)
    meta_cache_contents = meta_cache_manager.read_json() if meta_cache_manager.is_functional() else {}
    metadata = pipe.get_fs_submission(query_name)

    reformatted_terminal_id = {}
    attributes = query_dict["attributes"]
    relationships = query_dict["relationships"]

    for entry in metadata:
        attr_idx = 0
        # While loop pairs keys and values and updates reformatted_terminal_id
        while(attr_idx < len(attributes)):
            key_name = relationships[attributes[attr_idx]]
            attr_idx += 1
            value_name = relationships[attributes[attr_idx]]
            attr_idx += 1
            data_key = str(entry[key_name])
            reformatted_terminal_id[data_key] = str(entry[value_name])

    # for entry in reformatted_terminal_id:
    #     print("\n", entry, reformatted_terminal_id[entry])
    #     # pass
    # print("\n")

    # Add the query metadata if the entry doesn't exist, otherwise update it
    meta_cache_contents.update({query_name: reformatted_terminal_id})
    # Write the updated json to the cache file
    meta_cache_manager.write_json(meta_cache_contents, cache_path)
    return reformatted_terminal_id


def get_meta_for_query(query_name, query_json_path="settings.json", meta_json_path="meta_cache.json"):
    query_manager = file_manager(query_json_path)
    meta_manager = file_manager(meta_json_path)
    if query_manager.is_functional():
        meta_reference = query_manager.read_json()["queries"][query_name]["meta_reference"]
        if meta_manager.is_functional():
            return meta_manager.read_json()[meta_reference]
        else:
            print("Meta manager is not functional")
    else:
        print("Query manager is not functional")
    # If the cache doesn't exist or if the query list doesn't exist, return None
    return None


"""Execute listener procedure

ONLY TO BE INSTANCED FROM MAIN OF SNS
"""
class listener_operator:

    __settings_path = None
    __settings_file = None

    __meta_json = None

    def __init__(self, settings_path, meta_json=None):

        self.__settings_path = settings_path
        self.__settings_file = file_manager(self.__settings_path)

        # TODO: Enforce Modularity
        self.__meta_json = meta_json

        if self.__settings_file.is_functional():
            self.__conduct_listening()
        else:
            print("Cannot Conduct Listening Due to Settings File Issue")

    def __conduct_listening(self):

        CREDENTIALS_FILE_PATH = "credentials.json"
        ID_CACHE_PATH = "generic_id_cache.json"

        gb_pipe_manager = pipe_manager(CREDENTIALS_FILE_PATH, self.__settings_path)

        # Listener operation

        # TODO: Implement listener and regulate data submissions
        listener_managers = []
        connector = gb_pipe_manager.get_pipe()
        settings_json = self.__settings_file.read_json()
        for query in settings_json["queries"]:
            query_json = settings_json["queries"][query]
            idm_instance = id_manager(query, ID_CACHE_PATH, self.__settings_path)
            if not query_json["meta"]:
                meta_dict = get_meta_for_query(query)
                listener_managers.append(listener_manager(listener(connector, query_json, query, idm_instance, meta_dict)))


"""Establish an active listener and pipe between the GB backend and CaaS-FS frontend

Connection to the FS requires access to a user's Google API service key.
Under credentials.json, populate the googleAuthPath field with the absolute path
to your Google API service key JSON.
"""
def main():

    SETTINGS_FILE_PATH = "settings.json"
    settings_manager = file_manager(SETTINGS_FILE_PATH)

    # Create parser object, and add arguments
    parser = argparse.ArgumentParser(description='Creates a listener for the FireStore')
    parser.add_argument('-fl', '--flush', dest='flush_output', action='store_true', help='Flush the transaction id cache')
    parser.add_argument('-fr', '--firstrun', dest='first_run', nargs='*', help='Runs the initial setup steps for the listener')

    # Handle execution of arguments
    args = parser.parse_args()
    if args.flush_output:
        first_run_operator.flush_cache()

    if args.first_run is not None:
        if settings_manager.is_functional():
            settings_json = settings_manager.read_json()
            is_all = 'all' in args.first_run
            # TODO: Better arg handling - rm 'transactions'
            for query in settings_json["queries"]:
                print(query)
                if (is_all or query in args.first_run):
                    print("Starting First Run for Query:", query)

                    # handle special non-meta cases as necessary
                    # if settings_json["queries"][query]["exclusion"] == "identity":
                    #     fr_operator = first_run_operator(query, INTERNAL_IDENTITY_CACHE)
                    #     INTERNAL_IDENTITY_CACHE = fr_operator.get_internal_cache()
                    # else:
                    #     fr_operator = first_run_operator(query)

                    fr_operator = first_run_operator(query, settings_json["queries"][query]["meta"])

                    print("\nFirst Run Complete for Query:", query)
            print("\nCompleted First Run Procedures")
        else:
            print("Settings manager is not functional")

    # More Identity Insanity
    # gbpm = pipe_manager()
    # i_operator = identity_operator(INTERNAL_IDENTITY_CACHE, gbpm.get_pipe())

    # print(get_meta_for_query("transactions")) # DEBUG

    # Procedes to Spool Listeners
    # if settings_manager.is_functional():
    #     settings_json = settings_manager.read_json()
    #     for query in settings_json["queries"]:
    #         query_json = settings_json["queries"][query]
    #         if not query_json["meta"] and query_json["exclusion"] == None:
    #             meta_data = get_meta_for_query(query)
    #             # print("Not meta")
    #             l_operator = listener_operator(SETTINGS_FILE_PATH, meta_data)


# Main execution
if __name__ == "__main__":
    main()
