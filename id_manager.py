## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

"""Alphanumeric ID Generator for Transaction IDs

:author: Caden Koscinski
:see: https://docs.google.com/document/d/1xUzexyPlPzPKF-AyD4YANaQXwQlG5O7qDk0kZdyZ9us/edit
:see: settings.json
"""

from file_manager import file_manager


class id_manager:

    __characters = ['0','1','2','3','4','5','6','7','8','9',
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x','y','z']

    __query_id_cache_path = None
    __query_id_cache_file = None

    __settings_path = None
    __settings_file = None

    def __init__(self, query_name, id_cache_path="generic_id_cache.json", settings_path="settings.json"):
        self.__query_name = query_name
        self.__id_cache_path = id_cache_path
        self.__id_cache_file = file_manager(self.__id_cache_path)
        self.__settings_path = settings_path
        self.__settings_file = file_manager(self.__settings_path)
        self.__id_string = ""
        if self.__settings_file.is_functional():
            is_meta = self.__settings_file.read_json()["queries"][query_name]["meta"]
        if (not self.__id_cache_file.is_functional() or len(self.__id_cache_file.read_json().keys()) == 0) and not is_meta:
            print("Initializing id cache for:", query_name)
            self.__id_cache_file.write_json({query_name : {}})
        self.__functional = self.__id_cache_file.is_functional() and self.__settings_file.is_functional()


    def get_query_name(self):
        return self.__query_name

    def get_truncated_id_string(self):
        return self.__id_string

    def get_full_id_string(self):
        return self.get_standard_id_sections() + "-" + self.__id_string

    def get_standard_id_sections(self):
        settings_json = self.__settings_file.read_json()
        organization = settings_json["organization"]
        server = settings_json["server"]
        machine_brand = settings_json["machine_brand"]
        return organization + "-" + server + "-" + machine_brand

    # gb_terminal_json will need to be queried from the gbDB and populated
    def issue_id(self, observation_json, observation_reference=None, meta_json=None):
        cache_json = self.__id_cache_file.read_json()

        query_name = self.__query_name
        obs_id = None
        query_id = None
        if meta_json is not None:
            meta_id = observation_json[observation_reference]
            gb_serial = meta_json[str(meta_id)]

            if gb_serial in cache_json[query_name]:
                obs_id = cache_json[query_name][gb_serial][observation_reference]
                query_id = self.__increment_id(cache_json[query_name][gb_serial][f"last_{query_name}"])
                cache_json[query_name][gb_serial][f"last_{query_name}"] = query_id
            else:
                # Adds new entry to the cache for each identified machine
                # print(len(cache_json[query_name]))
                if len(cache_json[query_name]) != 0:
                    obs_id = self.__increment_id(cache_json[query_name][f"last_{observation_reference}"])
                else:
                    obs_id = "000000"
                cache_json[query_name][f"last_{observation_reference}"] = obs_id
                cache_json[query_name][gb_serial] = {}
                # cache_json[query_name][gb_serial]["brand"] = machine_brand
                cache_json[query_name][gb_serial][observation_reference] = cache_json[query_name][f"last_{observation_reference}"]
                query_id = "000000"
                cache_json[query_name][gb_serial][f"last_{query_name}"] = query_id

            self.__id_string = obs_id + "-" + query_id
        else:
            if query_name in cache_json.keys():
                new_id = self.__increment_id(cache_json[query_name][f"last_{query_name}"])
            else:
                new_id = "000000"
            self.__id_string = new_id
            cache_json.update({query_name: {f"last_{query_name}": new_id}})

        # Update cache
        self.__id_cache_file.write_json(cache_json)
        return self.get_full_id_string()


    def __increment_id(self, current_id):

        current_id = list(current_id)

        id_length = len(current_id)
        characters_length = len(self.__characters)

        is_at_max = True
        for id_digit in current_id:
            if id_digit is not self.__characters[-1]:
                is_at_max = False

        if is_at_max:
            return "Overflow"

        scanned_index = id_length - 1;

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

    def update_dictionary_via_string(self, path, json_dict):
        path_list = path.split("-")
        if len(path_list) < 2:
            print("Entered path for dictionary was empty")
            return {}
        elif len(path_list) == 2:
            json_dict.update({path_list[0] : path_list[1]})
        else:
            current_key = path_list[0]
            if current_key not in json_dict.keys():
                json_dict.update({current_key : {}})
            json_dict.update({current_key : self.update_dictionary_via_string('-'.join(path_list[1:]), json_dict[current_key])})
        return json_dict


    def get_dictionary_content_via_path(self, path, json_dict):
        path_list = path.split("-")
        if len(path_list) < 1:
            print("Entered path for dictionary was empty")
            return None

        current_key = path_list[0]
        if current_key in json_dict.keys():
            if len(path_list) == 1:
                return json_dict[current_key]
            else:
                return self.get_dictionary_content_via_path('-'.join(path_list[1:]), json_dict[current_key])
        else:
            print(f"Key: \"{current_key}\" not found, returning closest dictionary found")
            return json_dict


    def update_cache_file_via_path(self, path_to_data, path_to_cache="generic_id_cache.json"):
        cache_manager = self.__id_cache_file
        cache_contents = cache_manager.read_json() if cache_manager.is_functional() else {}
        cache_contents = self.update_dictionary_via_string(path_to_data, cache_contents)
        cache_manager.write_json(cache_contents)


    def get_data_from_cache_via_path(self, path_to_data, path_to_cache="generic_id_cache.json"):
        cache_manager = self.__id_cache_file
        if cache_manager.is_functional():
            return self.get_dictionary_content_via_path(path_to_data, cache_manager.read_json())
        else:
            print(f"Cache at \"{path_to_cache}\" does not exist.")
            return None
