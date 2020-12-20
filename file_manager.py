"""File utility for converting .json files to proper format

:author Caden Koscinski:
"""

import json

class file_manager:

    __file_path = None
    __functional = True


    """Constructor
    :param file_path: absolute or relative file path
    """
    def __init__(self, file_path):
        self.__file_path = file_path
        # self.read_json()
        try:
            self.read_json()
        except:
            print("\nCannot Read the File at:", self.__file_path)
            self.__functional = False


    """Read the specified file
    :returns: dict of json-formatted file
    """
    def read_json(self):
        with open(self.__file_path) as f:
            file = json.load(f)
        return file


    def write_json(self, json_content, output_file_path=None):
        if output_file_path == None:
            output_file_path = self.__file_path
        with open(output_file_path, 'w') as f:
            json.dump(json_content, f)


    def is_functional(self):
        return self.__functional
