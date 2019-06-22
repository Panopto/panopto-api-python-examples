# Authorization for ID provider integration
This sample demonstrates how an ID provider can authorize Panopto REST API access on behalf of its users.
This is almost as same as [User Based Server Application example](../auth-user-based-app), but this creates the authentication code by using the application key of the ID provider.

This authorization is only intended for custom ID provider integration, and not recommended for any other purposes.
The application key enables access to the Panopto API as any user from that ID provider.

Most of authorization logic is in common code: [panopto_oauth2.py](../common/panopto_oauth2.py).

## Preparation
1. You need to be a Panopto site administrator.
2. If you do not have Python 3 on your system, install the latest stable version from https://python.org
3. Install external modules for this application.
```
pip install requests oauthlib requests_oauthlib
```

## Setup ID provider
Setup a new ID provider or pick an existing ID provider, and record its application ID.
Contact Panopto support for more detail information.

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
python sample.py --server [Panopto server name] --client-id [Client ID] --client-secret [Client Secret] --application-key [Applicatkon Key] --username [User name]
```
User name should include the prefix of ID provider name like ```NetID\John```.
This displays the list of folders that are accessible by the calling user, once per minute.
When this runs for more than an hour, which is the token expiration, it goes through the authorization again and retries.

## See also
Refer the top level [README.md](../README.md) for license, references, and additional notes.
