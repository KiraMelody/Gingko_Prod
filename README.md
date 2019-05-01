# BigCo #14: Gingko

## How to use our API?

The credibility score API is our main product. Advertisers and other users can query our API to get the score for a webpage/site before making their decisions (e.g. whether to deploy ads or not). To use the API, a user can simply send a http get request to our server with the target url attached. For example, using curl, a sample request can be sent by executing this command in shell:

`curl http://gingkoteam.tk/api?url=https://oakridgetoday.com/2019/04/27/realtylink-has-immediate-opportunity-for-self-storage-facility/#more-107383`

