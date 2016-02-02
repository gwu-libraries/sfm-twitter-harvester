# sfm-twitter-harvester
Harvesters for twitter content as part of Social Feed Manager.

[![Build Status](https://travis-ci.org/gwu-libraries/sfm-twitter-harvester.svg?branch=master)](https://travis-ci.org/gwu-libraries/sfm-twitter-harvester)

Provides harvesters for Twitter [REST API](https://dev.twitter.com/rest/public) and [Streaming API](https://dev.twitter.com/streaming/overview).

Harvesting is performed by [Twarc](https://github.com/edsu/twarc) and captured by a modified version of [WarcProx](https://github.com/gwu-libraries/warcprox).

## Installing
    git clone https://github.com/gwu-libraries/sfm-twitter-harvester.git
    cd sfm-twitter-harvester
    pip install -r requirements/requirements.txt

Note that `requirements/requirements.txt` references the latest releast of warcprox-gwu and sfm-utils.
If you are doing development on the interaction between warcprox-gwu, sfm-utils, and sfm-twitter-harvester,
use `requirements/dev.txt`. This uses a local copy of warcprox-gwu (`../warcprox`) and sfm-utils (`../sfm-utils`)
in editable mode.


## Running as a service
### Running as a service for the REST API.
The twitter harvester will act on harvest start messages received from the  *twitter_harvester* queue for REST harvests. To run as a service:

    python twitter_harvester.py service <mq host> <mq username> <mq password>

### Running as a service for the Streaming API.
The twitter harvester will act on harvest start and stop messages received from the *twitter_harvester* queue for streaming harvests. To run as a service:

    stream_consumer.py <mq host> <mq username> <mq password> twitter_harvester <comma-separated list of harvest start routing keys, e.g., harvest.start.twitter.twitter_filter> <filepath of twitter_harvester.py>
    
The twitter harvester uses [Supervisord](http://supervisord.org/) to run streaming harvests.  When it receives a harvest start message, it writes the harvest start message to a file and registers a new process with SupervisorD.  The process is executing the twitter harvester with the harvest start file.  When it receives a harvest stop message, it removes the process from SupervisorD, which terminates the running twitter harvester.

## Process harvest start files
The twitter harvester can process harvest start files. The format of a harvest start file is the same as a harvest start message.  To run without sending any messages:

    python twitter_harvester.py seed <path to file>

## Tests

### Unit tests
    python -m unittest discover

### Integration tests (inside docker containers)
1. Install [Docker](https://docs.docker.com/installation/) and [Docker-Compose](https://docs.docker.com/compose/install/).
2. Get a [twitter api key](https://apps.twitter.com/) and provide the key and secret to the tests. This can be done either by putting them in a file named `test_config.py` or in environment variables (`TWITTER_CONSUMER_KEY`,  `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN` and `TWITTER_ACCESS_TOKEN_SECRET`).  An example `test_config.py` looks like:

        TWITTER_CONSUMER_KEY = "EHdoTksBfgGflP5nUalEfhaeo"
        TWITTER_CONSUMER_SECRET = "ZtUpemtBkf2cEmaqiy52Dd343ihFu9PAiLebuMOmqN0QtXeAlen"
        TWITTER_ACCESS_TOKEN = "411876914-c2yZjbk1np0Z5MWEFYYQKSQNFFGBXd8T4k90YkJl"
        TWITTER_ACCESS_TOKEN_SECRET = "jK9QOmn5VRF5mfgAN6KgfmCKRqThXVQ1G6qQg8BCejvp"

2. Start up the containers.

        docker-compose -f docker/dev.docker-compose.yml up -d

3. Run the tests.

        docker exec docker_sfmtwitterstreamharvester_1 python -m unittest discover

4. Shutdown containers.

        docker-compose -f docker/dev.docker-compose.yml kill
        docker-compose -f docker/dev.docker-compose.yml rm -v --force
        

## Harvest start messages
Following is information necessary to construct a harvest start message for the twitter harvester.

For all harvest types:

Summary:

  * tweet

Extracted urls: Urls are extracted from `entities.url` and `entities.media`.

### Search harvest type

Type: twitter_search

Api methods called:

  * search/tweets

Required parameters:

  * token (for query)

Optional parameters:

  * incremental: True (default) or False

### Filter harvest type

Type: twitter_filter

Api methods called:

 * statuses/filter

Required parameters:

  * token (for track)

### Authentication

Required parameters:

  * consumer_key
  * consumer_secret
  * access_token
  * access_token_secret