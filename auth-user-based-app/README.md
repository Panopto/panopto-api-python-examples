# Authorization as User Based Server Application
This sample demonstrates the authorization process as a User Based Server Application.
It goes through the authorization process, then calls the 'get folder list' API as an example of accessing the Panopto REST API.

User Based Server Application is not recommended in general, because the application needs to handle user's password directly. It is still available in case the application needs to be used where end user cannot present at all.

Most of authorization logic is in common code: [panopto_oauth2.py](../common/panopto_oauth2.py).

## Preparation
1. You need a Panopto user account. If you don't have one, ask your organization's Panopto administrator.
2. If you do not have Python 3 on your system, install the latest stable version from https://python.org
3. Install external modules for this application.
```
pip install requests oauthlib requests_oauthlib
```

## Setup API Client on Panopto server
1. Sign in to the Panopto web site
2. Click the System icon at the left-bottom corner.
3. Click API Clients
4. Click New
5. Enter an arbitrary Client Name
6. Select User Based Server Application type.
7. Enter ```https://localhost``` into CORS Origin URL.
8. The rest can be blank. Click "Create API Client" button.
9. Note the created Client ID and Client Secret.

## Run the sample
Type the following command.
```
python sample.py --server [Panopto server name] --client-id [Client ID] --client-secret [Client Secret] --username [User name] --password [User's password]
```
This displays the list of folders that are accessible by the calling user, once per minute.
When this runs for more than an hour, which is the token expiration, it goes through the authorization again and retries.

## See also
Refer the top level [README.md](../README.md) for license, references, and additional notes.
