import json
import time
from file_manager import file_manager

class Listener:



    def __init__(self, table, activeColumn, pollInterval, columnList, connector, pageSize=100):
        self.__table = table
        self.__activeColumn = activeColumn
        self.__pollInterval = pollInterval
        self.__pageSize = pageSize
        self.__columnList = columnList
        self.__connector = connector
        self.__CACHE_FILE_PATH = "listenerCache.json"
        self.__CONF_FILE_PATH = "settings.json"
        self.__cache_manager = file_manager(CACHE_FILE_PATH)
        self.__conf_manager = file_manager(CONF_FILE_MANAGER)
        self.__cursor = self.__connector.cursor()

    def listen(self):
        # Need a string of columns that contains commas and spacing
        # Ex:
        columnList = ', '.join(self.__columnList)
        # TODO: Update this from the file....don't hardcode lastId
        lastId = 0
        while True:
            resultSetSize = 0
            while True:
                # TODO: Figure out proper caching for the interpolation after the > to actually work.
                query = ("SELECT {columnList} FROM {self.table} WHERE {self.activeColumn} > {See Comment Above} LIMIT {self.PageSize}")
                resultSet =  cursor.execute(query)
                resultSetSize = len(resultSet)
                lastId = resultSet.keys(-1)
                if resultSetSize > 0:
                    break
            time.sleep(self.__pollInterval)


## This needs more work but it's 4:11 and I'm tired. Will resume tomorrow.
