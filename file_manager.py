"""File utility for converting .json files to proper format

:author Caden Koscinski:
"""

import json

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
