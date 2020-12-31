## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

## Helper class for dealing with locally stored images and firebase store
## Primary Contributor: Noah

from firebase_admin import firestore, storage

class PictureHelper:

    # Ex Basic Usage: new PictureHelper("XXXXX-XXX-X-XXXXXXX-X-X", "DICPHCPMSMXOVEDK7_FRMTVBVD8ZSDRKKO")
    # Ex Adv. Usage: new PictureHelper("XXXXX-XXX-X-XXXXXXX-X-X", "DICPHCPMSMXOVEDK7_FRMTVBVD8ZSDRKKO.jpg", storage.bucket("your_link").ref.child("folder/file"), ".png")
    def __init__(self, firebase_filename, gb_filename, firebase_folder_ref = None, gb_filepath = None, extension = None):

        self.__firebase_filename = firebase_filename
        self.__gb_filename = gb_filename
        self.__file_type = firebase_filename[20]
        self.__handle_pictures();
        # https://firebase.google.com/docs/reference/admin/python/firebase_admin.storage
        # https://cloud.google.com/storage/docs/getting-bucket-information
        # https://console.cloud.google.com/storage/browser?authuser=1&project=fgcomplianceportal&prefix=
        # https://firebase.google.com/docs/reference/node/firebase.app
        self.__storage = storage.bucket("fgcomplianceportal.appspot.com")
        # https://firebase.google.com/docs/storage/web/create-reference#create_a_reference
        self.__storage_ref = self.__storage.ref()
        self.__firebase_folder_ref = None

        # Handle optional overrides

            # TODO: Add an error here if it is None but self.__file_type isn't 2 or 6
        if gb_filepath is None:
            if self.__file_type == '2':
                self.__gb_filepath = f"/batm/data/documents_unsorted/{self.__gb_filename}"
            elif self.__file_type == '6':
                self.__gb_filepath = f"/batm/data/captures/{self.__gb_filename}"
            # TODO: Add an error here if it is None but self.__file_type isn't 2 or 6
        else:
            self.__gb_filepath = gb_filepath
        if extension is None:
            self.__extension = ".jpg"
        else:
            self.__extension = extension

        # TODO: Add a check here to verify that the gb filepath/filename actually exists. If it doesn't throw an error.

        self.__firebase_filename = self.__firebase_filename + self.__extension

        if firebase_folder_ref is None:
            if self.__file_type == '2':
                self.__firebase_folder_ref = self.__storage_ref.child(f"id_pictures/{self.__firebase_filename}")
            elif self.__file_type == '6':
                self.__firebase_folder_ref = self.__storage_ref.child(f"customer_selfies/{self.__firebase_filename}")

        self.__handle_picture()


    def __handle_picture(self):
        # https://stackoverflow.com/questions/52883534/firebase-storage-upload-file-python

        blob = self.__storage.blob(self.__firebase_filename)
        with open(self.__gb_filepath) as file_obj:
            self.__firebase_folder_ref.put(file_obj)
            print("Sent a file to firestore:")
            print("     self.__gb_filepath: " + self.__gb_filepath)
            print("     self.__firebase_folder_ref: " + self.__firebase_folder_ref)
            print("     self.__firebase_filename: " + self.__firebase_filename)
            print("     self.__")

            # blob.upload_from_file(file_obj, self.__firebase_folder_ref)
