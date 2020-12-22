## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

## Helper class for dealing with locally stored images and firebase store
## Primary Contributor: Noah

class PictureHelper:

    # Ex: new PictureHelper("/id_pictures/", "XXXXX-XXX-X-XXXXXXX-X-X", "/batm/data/documents_unsorted/", "DICPHCPMSMXOVEDK7_FRMTVBVD8ZSDRKKO.jpg")
    def __init__(self, firebase_filename, gb_filename, firebase_filepath = None, gb_filepath = None, extension = None):
        
        self.__firebase_filename = firebase_filename
        self.__gb_filename = gb_filename
        self.__file_type = gb_filename[20]
        self.__handle_pictures();
        
        # Handle optional overrides
        if firebase_filepath is None:
            if self.__file_type == '2':
                self.__firebase_filepath = "/id_pictures/"
            elif self.__file_type == '6':
                self.__firebase_filepath = "/customer_selfies/"
            # TODO: Add an error here if it is None but self.__file_type isn't 2 or 6
        else:
            self.__firebase_filepath = firebase_filepath
        if gb_filepath is None:
            if self.__file_type == '2':
                self.__gb_filepath = "/batm/data/documents_unsorted/{self.__gb_filename}"
            elif self.__file_type == '6':
                self.__gb_filepath = "/batm/data/captures/{self.__gb_filename}"
            # TODO: Add an error here if it is None but self.__file_type isn't 2 or 6
        else:
            self.__gb_filepath = gb_filepath
        if extension is None:
            self.__extension = ".jpg"
        else:
            self.__extension = extension

        # TODO: Add a check here to verify that the gb filepath/filename actually exists. If it doesn't throw an error.
    
    def __handle_picture(self):
        