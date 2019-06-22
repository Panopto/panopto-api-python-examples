# Scheduled Recording Create/Read/Update/Delete
This sample demonstrates the Scheduled Recordings API. It creates, reads, updates, and then deletes a scheduled recording on a given recorder.

## Preparation
1. This examples uses the [Server-side Web Application](../auth-server-side-web-app) authentication. Follow the steps there.
2. You will need the name of a remote recorder you have access to.

## Run the sample
Type the following command.
```
python sample.py --server [Panopto server name] --client-id [Client ID] --client-secret [Client Secret] --recorder-name [Recorder name]
```
The program will authenticate, then create/read/update/delete a scheduled recording on the named recorder, printing the API's response each time.

This sample schedules a recording into the default folder of the remote recorder. The user who runs this sample needs to have creator permission to the folder.

## See also
Refer the top level [README.md](../README.md) for license, references, and additional notes.
