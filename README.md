<p align="center"><img src="https://raw.githubusercontent.com/freedomservicing/fs_branding/master/fs/fs_logo.jpg" alt="drawing" width="300"/></p>

# <p align="center"><b>gb_sns</b></p>
<p align="center"><b><i>General Bytes Database Scraper</i></b></p>

# Dependencies
* Make sure you have MySQL Connector/Python installed on your local system or the import wont work. You need to manually download this (probably)
    * Connector/Python can be downloaded from [here](https://dev.mysql.com/downloads/connector/python/).
* `pip install firebase_admin`
* You may need to install more:
    * `pip install python_jwt gcloud sseclient pycrypto requests-toolbelt`

# Dev Env
* The `launch.json` in `.vscode` should be cross-platform if you use VSCode for your environment.

# Special Notes
* **settings.json** - If a query has a subquery, then the subquery must be assigned first

# Code Copyright/License Notice
Copyright © 2020, Freedom Servicing LLC, All rights reserved.
