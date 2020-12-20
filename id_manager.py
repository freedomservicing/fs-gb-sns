"""Alphanumeric ID Generator for Transaction IDs

:author: Caden Koscinski
:see: https://docs.google.com/document/d/1xUzexyPlPzPKF-AyD4YANaQXwQlG5O7qDk0kZdyZ9us/edit
:see: settings.json
"""

from file_manager import file_manager

class id:

    __organization = None
    __server = None
    __brand = None
    __machine = None
    __transaction = None

    __properties_json = None

    __id_string = None

    def __init__(self, properties_json=None):
        self.__properties_json = properties_json
        if self.__properties_json != None:
            self.__build_id()

    def __build_id(self):
        self.__organization = self.__properties_json["organization"]
        self.__server = self.__properties_json["server"]
        self.__brand = self.__properties_json["brand"]
        self.__machine = self.__properties_json["machine"]
        self.__transaction = self.__properties_json["transaction"]
        self.__id_string = self.__format_id()

    def __format_id(self):
        return self.__organization + "-" + self.__server + "-" + self.__brand + "-" + self.__machine + "-" + self.__transaction

    def get_id_string(self):
        return self.__id_string

class id_manager:

    __characters = ['0','1','2','3','4','5','6','7','8','9',
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x','y','z']

    __transaction_id_cache_path = None
    __transaction_id_cache_file = None

    __settings_path = None
    __settings_file = None

    __functional = None

    def __init__(self, transaction_id_cache_path, settings_path):
        self.__transaction_id_cache_path = transaction_id_cache_path
        self.__transaction_id_cache_file = file_manager(self.__transaction_id_cache_path)
        self.__settings_path = settings_path
        self.__settings_file = file_manager(self.__settings_path)
        if self.__transaction_id_cache_file.is_functional() and self.__settings_file.is_functional():
            self.__functional = True


    # gb_terminal_json will need to be queried from the gbDB and populated
    def issue_id(self, observation_json, gb_terminal_json):

        organization = self.__settings_file.read_json()["organization"]
        server = self.__settings_file.read_json()["server"]
        machine_brand = self.__settings_file.read_json()["machine_brand"]

        gb_id = observation_json["machine_id"]
        gb_serial = gb_terminal_json[str(gb_id)]

        cache_json = self.__transaction_id_cache_file.read_json()

        machine_id = None
        transaction_id = None

        if gb_serial in cache_json["machines"]:
            machine_id = cache_json["machines"][gb_serial]["machine_id"]
            transaction_id = self.__increment_id(cache_json["machines"][gb_serial]["last_transaction_id"])
            cache_json["machines"][gb_serial]["last_transaction_id"] = transaction_id
        else:
            # Adds new entry to the cache for each identified machine
            if len(cache_json["machines"]) != 0:
                machine_id = self.__increment_id(cache_json["last_machine_id"])
            else:
                machine_id = cache_json["last_machine_id"]
            cache_json["last_machine_id"] = machine_id
            cache_json["machines"][gb_serial] = {}
            cache_json["machines"][gb_serial]["brand"] = machine_brand
            cache_json["machines"][gb_serial]["machine_id"] = cache_json["last_machine_id"]
            transaction_id = "000000"
            cache_json["machines"][gb_serial]["last_transaction_id"] = transaction_id

        # Update cache
        self.__transaction_id_cache_file.write_json(cache_json)

        nid = id({"organization": organization, "server": server, "brand": machine_brand, "machine": machine_id, "transaction": transaction_id})

        return nid.get_id_string()

    def __increment_id(self, current_id):

        current_id = list(current_id)

        id_length = len(current_id)
        characters_length = len(self.__characters)

        scanned_index = id_length - 1

        while scanned_index >= 0:
            current_character = current_id[scanned_index]

            if current_character != self.__characters[characters_length - 1]:
                current_id[scanned_index] = self.__characters[self.__characters.index(current_character) + 1]
                # Break Outer Loop - No need to continue scanning
                scanned_index = -1
            else:
                current_id[scanned_index] = self.__characters[0]
                scanned_index -= 1

        return "".join(current_id)
