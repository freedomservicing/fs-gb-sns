## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.
"""Listener Boi

:see: https://docs.google.com/document/d/1CmbGNYDnQZ6idU0OOlEq3P8plQmYn6p8NcZcOXrTZAw/edit
"""
import json
import time
from file_manager import file_manager
import threading

class listener:

    def __init__(self, connector, queryConfigJson, query_name, idm, meta_json):
        self.__connector = connector
        self.__queryConfigJson = queryConfigJson
        self.__query_name = query_name
        self.__idm = idm
        self.__meta_json = meta_json

        self.__table = self.__queryConfigJson["attributeTable"]
        self.__active_query_column = self.__queryConfigJson["listener_column"]
        self.__active_column = self.__queryConfigJson["relationships"][self.__active_query_column]
        self.__pollInterval = self.__queryConfigJson["listener_interval"]

        if "page_size" in self.__queryConfigJson:
            self.__page_size = self.__queryConfigJson["page_size"]
        else:
            self.__page_size = 100

        # This should result in a list of columns seperated by commas and spaces
        # Ex: "id, amount, "
        self.__column_list = ', '.join(self.__queryConfigJson["attributes"])

        self.__CACHE_FILE_PATH = "listener_cache.json"
        self.__cache_manager = file_manager(self.__CACHE_FILE_PATH)

        self.__endpoint = self.__queryConfigJson["endpoint"]

        # An ID for logging purposes. Ex: listener_transactions_id_60
        self.__listener_id = f"listener_{self.__table}_{self.__active_column}_{self.__pollInterval}"

        self.__tracked_value = None

        self.__functional = self.__cache_manager.is_functional()

    def listen(self):

        master_cache = self.__cache_manager.read_json()
        listener_records = master_cache["listener_record"]

        if self.__query_name not in listener_records:
            listener_records[self.__query_name] = {"last_id": 0}
            master_cache["listener_record"] = listener_records

        current_cache = listener_records[self.__query_name]
        self.__tracked_value = current_cache["last_id"]

        while True:

            resultSetSize = 0

            while True:

                query = self.__connector.get_query(self.__query_name)
                listener_ext = f" WHERE {self.__active_query_column}>{self.__tracked_value} LIMIT {self.__page_size}"

                # print("\nL-Ext:", listener_ext)

                query += listener_ext

                # print("\nL-Query:", query)

                results = self.__connector.restructure_query_response(self.__query_name, self.__connector.submit_query(query))
                sanitized_results = self.__connector.prepare_fs_submission(results, self.__query_name)

                sr_size = len(sanitized_results)

                if sr_size > 0:
                    print("\nAdding", sr_size, "Entries after", self.__tracked_value)

                    self.__tracked_value = sanitized_results[sr_size - 1][self.__active_column]
                    self.__connector.commit_data(sanitized_results, self.__endpoint, self.__idm, self.__meta_json)

                    master_cache["listener_record"][self.__query_name]["last_id"] = self.__tracked_value

                    self.__cache_manager.write_json(master_cache)
                else:
                    print("\nNo New Entries Detected...")

                if resultSetSize > 0:
                    break
            time.sleep(self.__pollInterval)

    def update_current_cache(self):
        pass

    def get_listener_id(self):
        return self.__listener_id

    def is_functional(self):
        return self.__functional

## This needs more work but it's 4:11 and I'm tired. Will resume tomorrow.

class listener_manager:

    __listener = None

    def __init__(self, listener):
        self.__listener = listener
        if self.__listener.is_functional():
            self.__initiate_listener()
        else:
            print("\nUnable to Spool Listener:", self.__listener.get_listener_id)

    def __initiate_listener(self):
        try:
            new_listener_thread = threading.Thread(target=self.__listener.listen)
            new_listener_thread.start()
        except:
            print("Unable to Start Thread for Listener:", self.__listener.get_listener_id())
