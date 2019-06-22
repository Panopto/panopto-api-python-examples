# Panopto REST API Examples with Python 3

This repository includes examples that demonstrate how Panopto's REST API can be used with Python 3.

- [auth-server-side-web-app](auth-server-side-web-app): Authorization as Server-side Web Application
- [auth-user-based-app](auth-user-based-app): Authorization as User Based Server Application
- [auth-id-provider](auth-id-provider): Authorization for ID provider integration
- [common](common): Shared code used by multiple examples
- [folders-cli](folders-cli): Command line application with Folders API
- [scheduled-recording-crud](scheduled-recording-crud): Create/read/update/delete via Scheduled Recording API.
- [sessions-cli](sessions-cli): Command line application with Sessions API

## Warning
Those samples do not necessarily implement complete error handling or retry logic. As the best practice, you should have both proper error handling and reasonable retry logic in production code.

## Capture traffic
It is useful to capture the actual network traffic with a capture tool, like [Fiddler on Windows](https://www.telerik.com/fiddler) or [Charles on Mac](https://www.charlesproxy.com/), and examine it.
The samples in repository generally accept ```--skip-verify``` option for that purpose, so that they ignore the SSL certificate replaced by such tool and continue to run.

## References
- [Panopto Public API documentation](https://demo.hosted.panopto.com/Panopto/api/docs/index.html)
- Panopto support document: [Create OAuth2 Clients](https://support.panopto.com/s/article/oauth2-client-setup)
- Panopto support document: [OAuth2 Access Tokens For Services](https://support.panopto.com/s/article/oauth2-for-services)
- [Requests-OAuthlib](https://requests-oauthlib.readthedocs.io/): Python module to handle OAuth2 workflow on top of [OAuthlib library](https://github.com/oauthlib/oauthlib)
- [Requests](https://2.python-requests.org/): HTTP library for Python

## License
Copyright 2019 Panopto

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
