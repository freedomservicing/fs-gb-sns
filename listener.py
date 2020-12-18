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
        self.__activeColumn = self.__queryConfigJson["listener_column"]
        self.__pollInterval = self.__queryConfigJson["listener_interval"]

        if "page_size" in self.__queryConfigJson:
            self.__pageSize = self.__queryConfigJson["page_size"]
        else:
            self.__pageSize = 100

        # This should result in a list of columns seperated by commas and spaces
        # Ex: "id, amount, "
        self.__columnList = ', '.join(self.__queryConfigJson["attributes"])

        self.__CACHE_FILE_PATH = "listenerCache.json"
        self.__cache_manager = file_manager(self.__CACHE_FILE_PATH)
        self.__cursor = self.__connector.cursor()

        self.__endpoint = self.__queryConfigJson["endpoint"]

        # An ID for logging purposes. Ex: listener_transactions_id_60
        self.__listener_id = "listener_{self.__table}_{self.__activeColumn}_${self.__pollInterval}"

    def listen(self):
        # Need a string of columns that contains commas and spacing
        # Ex:

        # TODO: Update this from the file....don't hardcode lastId
        lastId = 0
        while True:
            resultSetSize = 0
            while True:
                # TODO: Figure out proper caching for the interpolation after the > to actually work.
                query = ("SELECT {columnList} FROM {self.table} WHERE {self.activeColumn} > {See Comment Above} LIMIT {self.PageSize}")
                resultSet =  self.__cursor.execute(query)
                resultSetSize = len(resultSet)
                lastId = resultSet.keys(-1)

                resultSet = self.__connector(resultSet, self.__query_name)

                self.__connector.commit_data(resultSet, self.__endpoint, self.__idm, self.__meta_json)

                if resultSetSize > 0:
                    break
            time.sleep(self.__pollInterval)

    def get_listener_id(self):
        return self.__listener_id

## This needs more work but it's 4:11 and I'm tired. Will resume tomorrow.

class listener_manager:

    __listener = None

    def __init__(self, listener):
        self.__listener = listener
        self.__initiate_listener()

    def __initiate_listener(self):
        try:
            new_listener_thread = threading.Thread(target=self.__listener.listen)
            new_listener_thread.start()
        except:
            print("Unable to Start Thread for Listener:", self.__listener.get_listener_id())
