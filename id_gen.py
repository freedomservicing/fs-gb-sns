"""Alphanumeric ID Generator for Transaction IDs

:author: Caden Koscinski
:see: https://docs.google.com/document/d/1xUzexyPlPzPKF-AyD4YANaQXwQlG5O7qDk0kZdyZ9us/edit
:see: settings.json
"""

from file_manager import file_manager

class id:

    __characters = {0,1,2,3,4,5,6,7,8,9,
    'a','b','c','d','e','f','g','h','i',
    'j','k','l','m','n','o','p','q','r',
    's','t','u','v','w','x','y','z'}

    __organization = None
    __brand = None
    __machine = None
    __transaction = None

    __settings_json = None

    def __init__(self, settings_json):
        self.__settings_json = settings_json
        self.__establish_properties()

    def __establish_properties(self):
        print()
