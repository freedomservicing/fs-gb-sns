import json
import time
from file_manager import file_manager

class Listener:

    

    def __init__(self, table, activeColumn, pollInterval, pageSize, columnList, connector):
        self.table = table
        self.activeColumn = activeColumn
        self.pollInterval = pollInterval
        self.pageSize = pageSize
        self.columnList = columnList
        self.connector = connector

    def listen(self):
        CACHE_FILE_PATH = "listenerCache.json"
        cache_manager = file_manager(CACHE_FILE_PATH)
        cursor = self.connector.cursor()
        query = ("SELECT {self.activeColumn} FROM {self.table}")
        columnList = ', '.join(self.columnList)
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
            time.sleep(self.pollInterval)
        
## This needs more work but it's 4:11 and I'm tired. Will resume tomorrow.
                

        
        



