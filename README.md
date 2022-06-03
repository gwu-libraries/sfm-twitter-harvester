# sfm-twitter-harvester
Harvesters for twitter content as part of [Social Feed Manager](https://gwu-libraries.github.io/sfm-ui).

[![Build Status](https://travis-ci.org/gwu-libraries/sfm-twitter-harvester.svg?branch=master)](https://travis-ci.org/gwu-libraries/sfm-twitter-harvester)

Provides harvesters for [Twitter v1 and v2 APIs](https://developer.twitter.com/en/docs/twitter-api/).

Harvesting is performed by [Twarc](https://github.com/edsu/twarc) and captured by a modified version of [WarcProx](https://github.com/gwu-libraries/warcprox).

## Development

For information on development and running tests, see the [development documentation](https://sfm.readthedocs.io/en/latest/development.html).

When running tests, provide Twitter credentials either as a `test_config.py` file or environment variables (`TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` and for the Twitter v2 API `TWITTER_BEARER_TOKEN`).  An example `test_config.py` looks like:

        TWITTER_CONSUMER_KEY = "EHdoTksBfgGflP5nUalEfhaeo"
        TWITTER_CONSUMER_SECRET = "ZtUpemtBkf2cEmaqiy52Dd343ihFu9PAiLebuMOmqN0QtXeAlen"
        TWITTER_ACCESS_TOKEN = "411876914-c2yZjbk1np0Z5MWEFYYQKSQNFFGBXd8T4k90YkJl"
        TWITTER_ACCESS_TOKEN_SECRET = "jK9QOmn5VRF5mfgAN6
        TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAAn6cn6sBA57n6uaABRalD7AIFEABxzAoj8F5MV%3DIxlklPFn3b1CDoLu0tSfbDaP6xvOo8ueJkbzH5u6nu0urAQwh6'

If only the v2 API is used, it is sufficient to configure the variable `TWITTER_BEARER_TOKEN`, the other variable need to be defined but may be empty.

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
  * media: True or False (default) to extract media urls
  * web_resources: True or False (default) to extract web resource urls
  
### User timeline harvest type

Type: twitter_user_timeline

Api methods called:

  * statuses/user_timeline
  * users/lookup (to lookup screen names and user ids)

Required parameters:

  * token (for screen name) and/or uid (for user id)

Optional parameters:

  * incremental: True (default) or False
  * media: True or False (default) to extract media urls
  * web_resources: True or False (default) to extract web resource urls
  
### Filter harvest type

Type: twitter_filter

Api methods called:

 * statuses/filter

Required parameters:

  * token: a dictionary containing track, follow, locations, and/or language
  
Optional parameters:

  * media: True or False (default) to extract media urls
  * web_resources: True or False (default) to extract web resource urls


### Sample harvest type

Type: twitter_sample

Api methods called:

 * statuses/sample

Optional parameters:

  * media: True or False (default) to extract media urls
  * web_resources: True or False (default) to extract web resource urls


### Authentication

Required parameters:

  * consumer_key
  * consumer_secret
  * access_token
  * access_token_secret
