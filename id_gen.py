"""Alphanumeric ID Generator for Transaction IDs

:author: Caden Koscinski
:see: https://docs.google.com/document/d/1xUzexyPlPzPKF-AyD4YANaQXwQlG5O7qDk0kZdyZ9us/edit
:see: settings.json
"""

from file_manager import file_manager

class id:

    __organization = None
    __brand = None
    __machine = None
    __transaction = None

    __properties_json = None

    __id_string = None

    def __init__(self, properties_json):
        self.__properties_json = properties_json
        self.__id_string = self.__establish_properties()

    def __build_id(self):
        self.__organization = self.__properties_json["organization"]
        self.__brand = self.__properties_json["brand"]
        self.__machine = self.__properties_json["machine"]
        self.__transaction = self.__properties_json["transaction"]
        return self.__organization + "-" + self.__brand + "-" + self.__machine + "-" + self.__transaction

    def get_id_string(self):
        return self.__id_string

class id_generator:

    __characters = ['0','1','2','3','4','5','6','7','8','9',
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x','y','z']

    __transaction_cache_path = None
    __transaction_cache_file = None

    __functional = True

    def __init__(self, transaction_cache_path):
        self.__transaction_cache_path = transaction_cache_path
        self.__transaction_cache_file = file_manager(self.__transaction_cache_path)
        self.__functional = self.__transaction_cache_file.is_functional()


    def increment_transaction_id(self):

        current_transaction_id = list(self.__transaction_cache_file.read_json()["last_transaction_id"])

        id_length = len(current_transaction_id)
        characters_length = len(self.__characters)

        scanned_index = id_length - 1

        while scanned_index >= 0:
            current_character = current_transaction_id[scanned_index]

            if current_character != self.__characters[characters_length - 1]:
                current_transaction_id[scanned_index] = self.__characters[self.__characters.index(current_character) + 1]
                # Break Outer Loop - No need to continue scanning
                scanned_index = -1
            else:
                current_transaction_id[scanned_index] = self.__characters[0]
                scanned_index -= 1

        current_transaction_id = "".join(current_transaction_id)

        writeJson = {"last_transaction_id": current_transaction_id}

        self.__transaction_cache_file.write_json(writeJson, self.__transaction_cache_path)

        return current_transaction_id
