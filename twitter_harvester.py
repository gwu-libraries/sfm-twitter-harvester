#!/usr/bin/env python3

from __future__ import absolute_import
from datetime import datetime, timedelta, timezone
import logging
import re
import json
import pytz
import requests
import threading #stream code

from twarc import Twarc, Twarc2
from twarc.decorators2 import _snowflake2millis, _millis2date
from sfmutils.harvester import BaseHarvester, Msg
from twitter_stream_warc_iter import TwitterStreamWarcIter
from twitter_stream_warc_iter import TwitterStreamWarcIter2
from twitter_rest_warc_iter import TwitterRestWarcIter, TwitterRestWarcIter2
from twarc import Twarc2, expansions  #stream code

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_harvester"

SEARCH_ROUTING_KEY = "harvest.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "harvest.start.twitter.twitter_user_timeline"
SEARCH2_ROUTING_KEY = "harvest.start.twitter2.twitter_search_2"
TIMELINE2_ROUTING_KEY = "harvest.start.twitter2.twitter_user_timeline_2"
ACADEMIC_SEARCH_ROUTING_KEY = "harvest.start.twitter2.twitter_academic_search"

status_re = re.compile("^https://twitter.com/.+/status/\d+$")

def since_id_to_timestamp(since_id):
    '''
    Convert a Twitter since_id to a tz-aware timestamp.
    :param since_id: an integer
    '''
    since_dt = _millis2date(_snowflake2millis(since_id))
    # Need to make this timestamp TZ aware (on the assumption that it's UTC to begin with)
    return since_dt.replace(tzinfo=timezone.utc)

def check_timedelta(timestamp, offset_days=7):
    '''
    Given a UTC timestamp, check its validity vis-a-vis the allowed window.
    :param timsetamp: a tz-aware datetime object in UTC timezone
    :param offset_days: the number of days prior to the current moment to check against the since_id
    '''
    today = datetime.now(timezone.utc)
    delta = timedelta(days=offset_days)
    # Is the timestamp more recent than offset_days?
    if today - delta <= timestamp:
        return timestamp
    else:
        return None

class TwitterHarvester(BaseHarvester):
    def __init__(self, working_path, stream_restart_interval_secs=30 * 60, mq_config=None, debug=False,
                 connection_errors=5, http_errors=5, debug_warcprox=False, tries=3):
        BaseHarvester.__init__(self, working_path, mq_config=mq_config,
                               stream_restart_interval_secs=stream_restart_interval_secs,
                               debug=debug, debug_warcprox=debug_warcprox, tries=tries)
        self.twarc = None
        self.connection_errors = connection_errors
        self.http_errors = http_errors

    def harvest_seeds(self):
        # Dispatch message based on type.
        harvest_type = self.message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            # Create a twarc
            self._create_twarc()
            self.search()
        elif harvest_type == "twitter_search_2":
            self._create_twarc2()
            self.search_2()
        elif harvest_type == "twitter_academic_search":
            self._create_twarc2()
            self.search_2(harvest_type=harvest_type)
        elif harvest_type == "twitter_filter":
            self._create_twarc()
            self.filter()
        elif harvest_type == "twitter_sample":
            self._create_twarc()
            self.sample()
        elif harvest_type == "twitter_user_timeline":
            self._create_twarc()
            self.user_timeline()
        elif harvest_type == "twitter_user_timeline_2":
            self._create_twarc2()
            self.user_timeline_2()

        #stream new code 

        elif harvest_type == "twitter_filter_stream":
            self._create_twarc2()
            self.stream_2()

        #stream new code ends  

        else:
            raise KeyError

    def _create_twarc(self):
        self.twarc = Twarc(self.message["credentials"]["consumer_key"],
                           self.message["credentials"]["consumer_secret"],
                           self.message["credentials"]["access_token"],
                           self.message["credentials"]["access_token_secret"],
                           http_errors=self.http_errors,
                           connection_errors=self.connection_errors,
                           tweet_mode="extended")

    def _create_twarc2(self):
        bearer_token = None
        if "bearer_token" in self.message["credentials"]:
            bearer_token = self.message["credentials"]["bearer_token"]
        self.twarc = Twarc2(self.message["credentials"]["consumer_key"],
                            self.message["credentials"]["consumer_secret"],
                            self.message["credentials"]["access_token"],
                            self.message["credentials"]["access_token_secret"],
                            bearer_token,
                            connection_errors=self.connection_errors,
                            metadata=True)

    def search(self):
        assert len(self.message.get("seeds", [])) == 1

        incremental = self.message.get("options", {}).get("incremental", False)

        since_id = self.state_store.get_state(__name__,
                                              u"{}.since_id".format(self._search_id())) if incremental else None

        query, geocode = self._search_parameters()
        self._harvest_tweets(self.twarc.search(query, geocode=geocode, since_id=since_id))
    

    def search_2(self, harvest_type="twitter_search_2"):
        '''
        :param harvest_type: str of the harvest type (to differentiate behaviors between search_recent and search_all (Academic Search))
        '''

        assert len(self.message.get("seeds", [])) == 1

        incremental = self.message.get("options", {}).get("incremental", False)

        since_id = self.state_store.get_state(__name__,
                                              u"{}.since_id".format(self._search_id())) if incremental else None
        query, geocode, start_time, end_time, limit = self._search_parameters2()
        # Checks necessary for the search_recent endpoint
        if (harvest_type == "twitter_search_2"):
            # If since_id is older than 7 days, ignore
            if since_id and not check_timedelta(since_id_to_timestamp(since_id)):
                since_id = None
            # Ignore the start_time param if outside the window for recent searches
            # Twitter seems to just ignore the end_time if outside the window
            if start_time:
                start_time = check_timedelta(start_time)
        # v.2 API does not allow the conjunction of start/end_time params with since_id
        # Let since_id take precedence
        if since_id:
            start_time, end_time = None, None
        if self.message.get("options").get("twitter_academic_search", False):
            if geocode is not None:
                query = "".join([query, " point_radius:[", geocode,"]"])
            self._harvest_tweets_2(self.twarc.search_all(query, since_id=since_id, start_time=start_time, end_time=end_time, max_results=100), limit)
        elif geocode is None:
            self._harvest_tweets_2(self.twarc.search_recent(query, since_id=since_id, start_time=start_time, end_time=end_time, max_results=100), limit)
        else:
            log.error("geocodes only supported in Twitter API v2 for Academic Research")

    def _search_parameters(self):
        if type(self.message["seeds"][0]["token"]) is dict:
            query = self.message["seeds"][0]["token"].get("query")
            geocode = self.message["seeds"][0]["token"].get("geocode")
        else:
            query = self.message["seeds"][0]["token"]
            geocode = None
        return query, geocode

    def _search_parameters2(self):
        if type(self.message["seeds"][0]["token"]) is dict:
            query = self.message["seeds"][0]["token"].get("query")
            geocode = self.message["seeds"][0]["token"].get("geocode")
            if self.message["seeds"][0]["token"].get("start_time"):
                start_time = datetime.fromisoformat(self.message["seeds"][0]["token"]["start_time"]).astimezone(pytz.utc)
            else: 
                start_time = None
            if self.message["seeds"][0]["token"].get("end_time"):
                end_time = datetime.fromisoformat(self.message["seeds"][0]["token"]["end_time"]).astimezone(pytz.utc)
            else: 
                end_time = None
            limit = self.message["seeds"][0]["token"].get("limit")
        else:
            query = self.message["seeds"][0]["token"]
            geocode = None
            start_time = None
            end_time = None
            limit = None

        return query, geocode, start_time, end_time, limit

    def _search_id(self):
        query, geocode = self._search_parameters()
        if query and not geocode:
            return query
        if geocode and not query:
            return geocode
        return ":".join([query, geocode])

    def filter(self):
        assert len(self.message.get("seeds", [])) == 1

        track = self.message["seeds"][0]["token"].get("track")
        follow = self.message["seeds"][0]["token"].get("follow")
        locations = self.message["seeds"][0]["token"].get("locations")
        language = self.message["seeds"][0]["token"].get("language")

        self._harvest_tweets(
            self.twarc.filter(track=track, follow=follow, locations=locations, lang=language, event=self.stop_harvest_seeds_event))


    #New stream rule




    def stream_2(self):

        
        '''
        # remove any active stream rules
        rules = self.twarc.get_stream_rules()
        if "data" in rules and len(rules["data"]) > 0:
            rule_ids = [r["id"] for r in rules["data"]]
            self.twarc.delete_stream_rule_ids(rule_ids)

        # make sure they are empty
        rules = self.twarc.get_stream_rules()
        assert "data" not in rules

        # add two rules
        rules = self.twarc.add_stream_rules(
            [{"value": "twitter", "tag": "modwarc-test"}, {"value": "musk", "tag": "tdwarc-test"}]
        )
        assert len(rules["data"]) == 2

        # make sure they are there
        #rules = self.twarc.get_stream_rules()
        #assert len(rules["data"]) == 2

        #print("rules",rules)

        #log.debug("rules Adhithya Kiran",rules["data"])
        #log.debug("rules lenght Adhithya Kiran",len(rules["data"]))
        '''
        e = threading.Event()
        #self._harvest_tweets_2(self.twarc.stream(event=e,record_keepalive=False),limit=100)
        self._process_tweets_stream(self.twarc.stream(event=e,record_keepalive=False),limit=500)

        #self._harvest_tweets_2(self.twarc.stream(event=e,record_keepalive=False),limit=500)

        
        
        
        
        

        #self._harvest_tweets_2(self.twarc.stream())

        
    #This is working using direct call

    # collect some data 
        #for count, result in enumerate(self.twarc.stream()):
        # The Twitter API v2 returns the Tweet information and the user, media etc.  separately
        # so we use expansions.flatten to get all the information in a single JSON
            #tweet = expansions.flatten(result)
        # Here we are printing the full Tweet object JSON to the console
            #print(json.dumps(tweet))
            #log.debug("json.dumps(tweet)",json.dumps(tweet))
        # Replace with the desired number of Tweets
            #if count > 10:
                #break


        


    #end of stream rules

    def sample(self):
        self._harvest_tweets(self.twarc.sample(self.stop_harvest_seeds_event))

    def user_timeline(self):
        incremental = self.message.get("options", {}).get("incremental", False)

        for seed in self.message.get("seeds", []):
            seed_id = seed["id"]
            screen_name = seed.get("token")
            user_id = seed.get("uid")
            log.debug("Processing seed (%s) with screen name %s and user id %s", seed_id, screen_name, user_id)
            assert screen_name or user_id

            # If there is not a user_id, look it up.
            if screen_name and not user_id:
                result, user = self._lookup_user(screen_name, "screen_name")
                if result == "OK":
                    user_id = user["id_str"]
                    self.result.uids[seed_id] = user_id
                else:
                    msg = u"User id not found for {} because account is {}".format(screen_name,
                                                                                   self._result_to_reason(result))
                    log.exception(msg)
                    self.result.warnings.append(Msg("token_{}".format(result), msg, seed_id=seed_id))
            # Otherwise, get the current screen_name
            else:
                result, user = self._lookup_user(user_id, "user_id")
                if result == "OK":
                    new_screen_name = user["screen_name"]
                    if new_screen_name and new_screen_name != screen_name:
                        self.result.token_updates[seed_id] = new_screen_name
                else:
                    msg = u"User {} (User ID: {}) not found because account is {}".format(screen_name, user_id,
                                                                                          self._result_to_reason(
                                                                                              result))
                    log.exception(msg)
                    self.result.warnings.append(Msg("uid_{}".format(result), msg, seed_id=seed_id))
                    user_id = None

            if user_id:
                # Get since_id from state_store
                since_id = self.state_store.get_state(__name__,
                                                      "timeline.{}.since_id".format(
                                                          user_id)) if incremental else None

                self._harvest_tweets(self.twarc.timeline(user_id=user_id, since_id=since_id))

    def user_timeline_2(self):
        incremental = self.message.get("options", {}).get("incremental", False)

        for seed in self.message.get("seeds", []):
            seed_id = seed["id"]
            screen_name = seed.get("token")
            user_id = seed.get("uid")
            log.debug("Processing seed (%s) with screen name %s and user id %s", seed_id, screen_name, user_id)
            assert screen_name or user_id

            # If there is not a user_id, look it up.
            if screen_name and not user_id:
                result, user = self._lookup_user_2(screen_name, "screen_name")
                if result == "OK":
                    user_id = user["id"]
                    self.result.uids[seed_id] = user_id
                else:
                    msg = u"User id not found for {} because account is {}".format(screen_name,
                                                                                   self._result_to_reason(result))
                    log.exception(msg)
                    self.result.warnings.append(Msg("token_{}".format(result), msg, seed_id=seed_id))
            # Otherwise, get the current screen_name
            else:
                result, user = self._lookup_user_2(user_id, "user_id")
                if result == "OK":
                    new_screen_name = user["username"]
                    if new_screen_name and new_screen_name != screen_name:
                        self.result.token_updates[seed_id] = new_screen_name
                else:
                    msg = u"User {} (User ID: {}) not found because account is {}".format(screen_name, user_id,
                                                                                          self._result_to_reason(
                                                                                              result))
                    log.exception(msg)
                    self.result.warnings.append(Msg("uid_{}".format(result), msg, seed_id=seed_id))
                    user_id = None

            if user_id:
                # Get since_id from state_store
                since_id = self.state_store.get_state(__name__,
                                                      "timeline.{}.since_id".format(
                                                          user_id)) if incremental else None

                self._harvest_tweets_2(self.twarc.timeline(user=user_id, since_id=since_id))

    def _lookup_user(self, id, id_type):
        url = "https://api.twitter.com/1.1/users/show.json"
        params = {id_type: id}

        # USER_DELETED: 404 and {"errors": [{"code": 50, "message": "User not found."}]}
        # USER_PROTECTED: 200 and user object with "protected": true
        # USER_SUSPENDED: 403 and {"errors":[{"code":63,"message":"User has been suspended."}]}
        result = "OK"
        user = None
        try:
            resp = self.twarc.get(url, params=params, allow_404=True)
            user = resp.json()
            if user['protected']:
                result = "unauthorized"
        except requests.exceptions.HTTPError as e:
            try:
                resp_json = e.response.json()
            except json.decoder.JSONDecodeError:
                raise e
            if e.response.status_code == 404 and self._has_error_code(resp_json, 50):
                result = "not_found"
            elif e.response.status_code == 403 and self._has_error_code(resp_json, 63):
                result = "suspended"
            else:
                raise e
        return result, user

    def _lookup_user_2(self, id, id_type):
        # https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction
        #
        # USER_DELETED:   200 and {"errors": [{"title": "Not Found Error", ...,
        #                                      "type": "https://api.twitter.com/2/problems/resource-not-found"}]}
        # INVALID_USER:   400 Client Error: Bad Request
        # USER_PROTECTED: 200 and user object with "protected": True
        # USER_SUSPENDED: 200 and {"errors":[{"detail": "User has been suspended: ...",
        #                                     "title": "Forbidden",
        #                                     "type": "https://api.twitter.com/2/problems/resource-not-found"}]}
        url = 'https://api.twitter.com/2/users/'
        if id_type == "screen_name":
            url = 'https://api.twitter.com/2/users/by/username/'
        url += id + '?user.fields=protected'
        result = "OK"
        user = None
        try:
            resp = self.twarc.get(url)
            res = resp.json()
            if 'data' in res:
                user = res['data']
                if user['protected']:
                    result = "unauthorized"
            elif 'errors' in res:
                result = 'unknown_error'
                if len(res['errors']) and 'detail' in res['errors'][0]:
                    if res['errors'][0]['detail'].startswith('Could not find user with ids:'):
                        result = "not_found"
                    elif res['errors'][0]['detail'].startswith('Could not find user with usernames:'):
                        result = "not_found"
                    elif res['errors'][0]['detail'].startswith('User has been suspended:'):
                        result = "suspended"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                result = "not_found"
            elif e.response.status_code == 400:
                # Bad Request, could be an invalid user name or id
                result = "not_found"
            else:
                raise e
        return result, user
 
    @staticmethod
    def _has_error_code(resp, code):
        if isinstance(code, int):
            code = (code,)
        for error in resp['errors']:
            if error['code'] in code:
                return True
        return False

    @staticmethod
    def _result_to_reason(result):
        if result == "unauthorized":
            return "protected"
        elif result == "suspended":
            return "suspended"
        return "not found or deleted"

    def _harvest_tweets(self, tweets):
        # max_tweet_id = None
        for count, tweet in enumerate(tweets):
            if not count % 100:
                log.debug("Harvested %s tweets", count)
            self.result.harvest_counter["tweets"] += 1
            if self.stop_harvest_seeds_event.is_set():
                log.debug("Stopping since stop event set.")
                break

    def _harvest_tweets_2(self, tweets, limit=None):
        # max_tweet_id = None
        # Counter for paginated tweets
        for i, page in enumerate(tweets):        
            
            if 'data' not in page:
                return
            for count, tweet in enumerate(page['data']):
                if not (count + 1) % 100:
                    log.debug("Harvested %s tweets", (count + 1) * (i + 1))
                self.result.harvest_counter["tweets"] += 1
                if limit and self.result.harvest_counter["tweets"] >= limit:
                    log.debug("Stopping since limit reached.")
                    self.stop_harvest_seeds_event.set()
                    #break
                if self.stop_harvest_seeds_event.is_set():
                    log.debug("Stopping since stop event set.")
                    break
            else:
                continue  
            break


    # for stream

    def _process_tweets_stream(self, tweets,limit=None):
        max_tweet_id = None
        for count, tweet in enumerate(tweets):
            if not count % 100:
                log.debug("Harvested %s tweets", count)
            self.result.harvest_counter["tweets"] += 1    
            if limit and self.result.harvest_counter["tweets"] >= limit:
                log.debug("Stopping since limit reached.")
                self.stop_harvest_seeds_event.set()                
            if self.stop_harvest_seeds_event.is_set():
                log.debug("Stopping since stop event set.")
                break
            else:
                continue


    #end for stream        



    def process_warc(self, warc_filepath):
        # Dispatch message based on type.
        harvest_type = self.message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            self.process_search_warc(warc_filepath)
        elif harvest_type == "twitter_search_2":
            self.process_search_warc_2(warc_filepath)
        elif harvest_type == "twitter_academic_search":
            self.process_search_warc_2(warc_filepath)
        elif harvest_type == "twitter_filter":
            self._process_tweets(TwitterStreamWarcIter(warc_filepath))
        #code for filter stream
        elif harvest_type == "twitter_filter_stream":
            self._process_tweets_2(TwitterStreamWarcIter2(warc_filepath))
        #code end for for filter stream
        elif harvest_type == "twitter_sample":
            self._process_tweets(TwitterStreamWarcIter(warc_filepath))
        elif harvest_type == "twitter_user_timeline":
            self.process_user_timeline_warc(warc_filepath)
        elif harvest_type == "twitter_user_timeline_2":
            self.process_user_timeline_warc_2(warc_filepath)
        else:
            raise KeyError

    def process_search_warc(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)

        since_id = self.state_store.get_state(__name__,
                                              u"{}.since_id".format(self._search_id())) if incremental else None
       
        max_tweet_id = self._process_tweets(TwitterRestWarcIter(warc_filepath))

        # Update state store
        if incremental and (max_tweet_id or 0) > (since_id or 0):
            self.state_store.set_state(__name__, u"{}.since_id".format(self._search_id()), max_tweet_id)

    def process_search_warc_2(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)

        since_id = self.state_store.get_state(__name__,
                                              u"{}.since_id".format(self._search_id())) if incremental else None

        max_tweet_id = self._process_tweets_2(TwitterRestWarcIter2(warc_filepath))

        # Update state store
        if incremental and (max_tweet_id or 0) > (since_id or 0):
            self.state_store.set_state(__name__, u"{}.since_id".format(self._search_id()), max_tweet_id)

    def process_user_timeline_warc(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)

        for count, status in enumerate(TwitterRestWarcIter(warc_filepath)):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet or "full_text" in tweet:
                user_id = tweet["user"]["id_str"]
                if incremental:
                    # Update state
                    key = "timeline.{}.since_id".format(user_id)
                    self.state_store.set_state(__name__, key,
                                               max(self.state_store.get_state(__name__, key) or 0, tweet.get("id")))
                self._process_tweet(tweet)
 
    def process_user_timeline_warc_2(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)

        for count, status in enumerate(TwitterRestWarcIter2(warc_filepath)):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet:
                user_id = tweet["author_id"]
                if incremental:
                    # Update state
                    key = "timeline.{}.since_id".format(user_id)
                    self.state_store.set_state(__name__, key,
                                               max(self.state_store.get_state(__name__, key) or 0,
                                                   int(tweet.get("id"))))
                self._process_tweet(tweet)

      
    def _process_tweets(self, warc_iter):
        max_tweet_id = None

        for count, status in enumerate(warc_iter):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet or "full_text" in tweet:
                max_tweet_id = max(max_tweet_id or 0, tweet.get("id"))
                self._process_tweet(tweet)
        return max_tweet_id
    
    def _process_tweets_2(self, warc_iter):
        max_tweet_id = None

        for count, status in enumerate(warc_iter):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet:
                max_tweet_id = max(max_tweet_id or 0,
                                   int(tweet.get("id")))
                self._process_tweet(tweet)
        return max_tweet_id

    def _process_tweet(self, _):
        self.result.increment_stats("tweets")


if __name__ == "__main__":
    TwitterHarvester.main(TwitterHarvester, QUEUE, [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY, SEARCH2_ROUTING_KEY, TIMELINE2_ROUTING_KEY, ACADEMIC_SEARCH_ROUTING_KEY])
