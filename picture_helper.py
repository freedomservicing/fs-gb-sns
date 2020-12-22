## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

## Helper class for dealing with locally stored images and firebase store
## Primary Contributor: Noah



class PictureHelper:


    # Ex: new PictureHelper("/id_pictures/", "XXXXX-XXX-X-XXXXXXX-X-X.jpg", "/batm/data/documents_unsorted/", "DICPHCPMSMXOVEDK7_FRMTVBVD8ZSDRKKO.jpg")
    def __init__(self, firebase_filename, gb_filename, firebase_filepath = None, gb_filepath = None, extension = None):
        self.__firebase_filename = firebase_filename
        self.__gb_filename = gb_filename
        self.__firebase_filepath = firebase_filepath
        self.__gb_filepath = gb_filepath
        self.__extension = extension
        self.__file_type = gb_filename[20]
        if self.__file_type == '2':
            self.__firebase_filepath = "/id_pictures/"
            self.__gb_filepath = "/batm/data/documents_unsorted/{self.__gb_filename}"
        elif self.__file_type == '6':
            self.__firebase_filepath = "/customer_selfies/"
            self.__gb_filepath = "/batm/data/captures/{self.__gb_filename}"
        else:
            ##TODO: Write code to have a descriptive error here.

