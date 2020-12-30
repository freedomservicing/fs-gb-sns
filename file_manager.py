## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

"""File utility for converting .json files to proper format

:author Caden Koscinski:
"""

import json

class file_manager:

    """Constructor
    :param file_path: absolute or relative file path
    """
    def __init__(self, file_path, fm_id = "Default"):
        self.__file_path = file_path
        self.__fm_id = fm_id
        self.__functional = True
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
        # if self.__fm_id != "Default":
        #     print("\nIn FM:", self.__fm_id, "\nFile Contents:", file)
        return file


    def write_json(self, json_content, output_file_path=None):
        if output_file_path == None:
            output_file_path = self.__file_path
        with open(output_file_path, 'w') as f:
            try:
                json.dump(json_content, f)
                self.__functional = True
            except:
                print("\nCannot write to file at:", self.__file_path)


    def is_functional(self):
        return self.__functional
