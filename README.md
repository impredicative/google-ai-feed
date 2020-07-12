# google-ai-feed
**google-ai-feed** uses Python 3.7 to serve a filtered RSS feed for Google AI publications.
As a disclaimer, it has no affiliation with Google.

## Links
* [Project repo](https://github.com/ml-feeds/google-ai-feed)
* [Upstream website](https://research.google/pubs/)
* [**Unofficial filtered feed**](https://us-east1-ml-feeds.cloudfunctions.net/google-ai)

## Deployment
Serverless deployment to [Google Cloud Functions](https://console.cloud.google.com/functions/) is configured.
It requires the following files:
* requirements.txt
* main.py (having callable `serve(request: flask.Request) -> Tuple[bytes, int, Dict[str, str]]`)

Deployment version updates are not automated.
They can be performed manually by editing and saving the function configuration.

These deployment links require access:
* [Dashboard](https://console.cloud.google.com/functions/details/us-east1/google-ai?project=ml-feeds)
* [Logs](https://console.cloud.google.com/logs?service=cloudfunctions.googleapis.com&key1=google-ai&key2=us-east1&project=ml-feeds)
* [Repo](https://source.cloud.google.com/ml-feeds/github_ml-feeds_google-ai-feed)
