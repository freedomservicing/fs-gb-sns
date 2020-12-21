<p align="center"><img src="https://raw.githubusercontent.com/freedomservicing/fs_branding/master/fs/fs_logo.jpg" alt="drawing" width="300"/></p>

# <p align="center"><b>gb_sns</b></p>
<p align="center"><b><i>Freedom Servicing General Bytes Database Scraper Tool</i></b></p>

![gb_sns_license](https://img.shields.io/github/license/freedomservicing/gb_sns?color=purple&style=flat-square) ![gb_sns_prs](https://img.shields.io/github/issues-pr-closed/freedomservicing/gb_sns?color=%234debc7&style=flat-square) ![gb_sns_open_issues](https://img.shields.io/github/issues-raw/freedomservicing/gb_sns?color=red&style=flat-square) ![gb_sns_closed_issues](https://img.shields.io/github/issues-closed-raw/freedomservicing/gb_sns?color=green&style=flat-square) ![gb_sns_last_commit](https://img.shields.io/github/last-commit/freedomservicing/gb_sns?style=flat-square) ![gb_sns_size](https://img.shields.io/github/repo-size/freedomservicing/gb_sns?style=flat-square) 

# Dependencies
* Make sure you have MySQL Connector/Python installed on your local system or the import wont work. You need to manually download this (probably)
    * Connector/Python can be downloaded from [here](https://dev.mysql.com/downloads/connector/python/).
* `pip install python_jwt gcloud sseclient pycrypto requests-toolbelt firebase_admin`

# Dev Env
* The `launch.json` in `.vscode` should be cross-platform if you use VSCode for your environment.

# Special Notes
* **settings.json** - If a query has a subquery, then the subquery must be assigned first

# Code Copyright/License Notice
Copyright © 2020, Freedom Servicing, LLC.

The Freedom Servicing General Bytes Database Scraper Tool (GB_SNS) is released under the terms of the MIT license. See LICENSE.md for more information or see https://opensource.org/licenses/MIT.
