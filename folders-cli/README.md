# Command line application with Folders API
This sample demonstrates the usage of the Folders API.

## Preparation
1. You need a Panopto user account. If you don't have it, ask your organization's Panopto administrator.
2. If you do not have Python 3 on your system, install the latest stable version from https://python.org
3. Install external modules for this application.
```
pip install requests oauthlib requests_oauthlib
```

## Setup API Client on Panopto server
See the instruction for [Authorization as Server-side Web Application](../auth-server-side-web-app/README.md)

## Run the sample
Type the following command.
```
python sample.py --server [Panopto server name] --client-id [Client ID] --client-secret [Client Secret]
```
This starts command line interaction of folder management, starting from the top level folder.

## See also
Refer the top level [README.md](../README.md) for license, references, and additional notes.
