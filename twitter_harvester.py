#!/usr/bin/env python

from __future__ import absolute_import
import logging
import re

from twarc import Twarc
from sfmutils.harvester import BaseHarvester, Msg, CODE_TOKEN_NOT_FOUND, CODE_TOKEN_UNAUTHORIZED
from twitter_stream_warc_iter import TwitterStreamWarcIter
from twitter_rest_warc_iter import TwitterRestWarcIter
from requests.exceptions import HTTPError

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_harvester"
SEARCH_ROUTING_KEY = "harvest.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "harvest.start.twitter.twitter_user_timeline"

status_re = re.compile("^https://twitter.com/.+/status/\d+$")


class TwitterHarvester(BaseHarvester):
    def __init__(self, working_path, stream_restart_interval_secs=30 * 60, mq_config=None, debug=False,
                 connection_errors=5, http_errors=5, debug_warcprox=False, tries=3):
        BaseHarvester.__init__(self, working_path, mq_config=mq_config,
                               stream_restart_interval_secs=stream_restart_interval_secs,
                               debug=debug, debug_warcprox=debug_warcprox, tries=tries)
        self.twarc = None
        self.connection_errors = connection_errors
        self.http_errors = http_errors
        self.extract_media = False
        self.extract_web_resources = False
        self.extract_user_profile_images = False

    def harvest_seeds(self):
        # Create a twarc
        self._create_twarc()

        # Get harvest extract options.
        self.extract_media = self.message.get("options", {}).get("media", False)
        self.extract_web_resources = self.message.get("options", {}).get("web_resources", False)
        self.extract_user_profile_images = self.message.get("options", {}).get("user_images", False)

        # Dispatch message based on type.
        harvest_type = self.message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            self.search()
        elif harvest_type == "twitter_filter":
            self.filter()
        elif harvest_type == "twitter_sample":
            self.sample()
        elif harvest_type == "twitter_user_timeline":
            self.user_timeline()
        else:
            raise KeyError

    def _create_twarc(self):
        self.twarc = Twarc(self.message["credentials"]["consumer_key"],
                           self.message["credentials"]["consumer_secret"],
                           self.message["credentials"]["access_token"],
                           self.message["credentials"]["access_token_secret"],
                           http_errors=self.http_errors,
                           connection_errors=self.connection_errors)

    def search(self):
        assert len(self.message.get("seeds", [])) == 1

        incremental = self.message.get("options", {}).get("incremental", False)
        query = self.message["seeds"][0]["token"]

        since_id = self.state_store.get_state(__name__, u"{}.since_id".format(query)) if incremental else None

        self._harvest_tweets(self.twarc.search(query, since_id=since_id))

    def filter(self):
        assert len(self.message.get("seeds", [])) == 1

        track = self.message["seeds"][0]["token"].get("track")
        follow = self.message["seeds"][0]["token"].get("follow")
        locations = self.message["seeds"][0]["token"].get("locations")

        self._harvest_tweets(
            self.twarc.filter(track=track, follow=follow, locations=locations, event=self.stop_harvest_seeds_event))

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
                user_id = self._lookup_user_id(screen_name)
                if user_id:
                    # Report back if nsid found
                    self.result.uids[seed_id] = user_id
                else:
                    msg = "User id not found for user {} because account is not found or suspended".format(screen_name)
                    log.exception(msg)
                    self.result.warnings.append(Msg(CODE_TOKEN_NOT_FOUND, msg))
            # Otherwise, get the current screen_name
            else:
                new_screen_name = self._lookup_screen_name(user_id)
                # if can't find the screen_name, ignore get timeline
                if not new_screen_name:
                    msg = "Screen name not found for user id {} because account is not found or suspended".format(
                        user_id)
                    log.exception(msg)
                    self.result.warnings.append(Msg(CODE_TOKEN_NOT_FOUND, msg))
                    # reset the user_id, ignore the get timeline
                    user_id = None
                if new_screen_name and new_screen_name != screen_name:
                    self.result.token_updates[seed_id] = new_screen_name
                    screen_name = new_screen_name

            if user_id:
                try:
                    # Get since_id from state_store
                    since_id = self.state_store.get_state(__name__,
                                                          "timeline.{}.since_id".format(
                                                              user_id)) if incremental else None

                    self._harvest_tweets(self.twarc.timeline(user_id=user_id, since_id=since_id))

                except HTTPError as e:
                    if e.response.status_code == 401:
                        account = "user {} (User ID: {})".format(screen_name,
                                                                 user_id) if screen_name else "user ID: {}".format(
                            user_id)
                        msg = "Unauthorized for {} because account is suspended or protected".format(account)
                        log.exception(msg)
                        self.result.warnings.append(Msg(CODE_TOKEN_UNAUTHORIZED, msg))
                    else:
                        raise e

    def _lookup_screen_name(self, user_id):
        """
        Lookup a screen name given a user id.
        """
        try:
            users = list(self.twarc.user_lookup(user_ids=(user_id,)))
            assert len(users) in (0, 1)
            if users:
                return users[0]["screen_name"]
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
        return None

    def _lookup_user_id(self, screen_name):
        """
        Lookup a user id given a screen name.
        """
        try:
            users = list(self.twarc.user_lookup(screen_names=(screen_name,)))
            assert len(users) in (0, 1)
            if users:
                return users[0]["id_str"]
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
        return None

    def _harvest_tweets(self, tweets):
        # max_tweet_id = None
        for count, tweet in enumerate(tweets):
            if not count % 100:
                log.debug("Harvested %s tweets", count)
            self.result.harvest_counter["tweets"] += 1
            if self.stop_harvest_seeds_event.is_set():
                log.debug("Stopping since stop event set.")
                break

    def _process_entities(self, entities):
        if self.extract_web_resources:
            for url in entities.get("urls", []):
                # Exclude links for tweets
                if url["expanded_url"] and not status_re.match(url["expanded_url"]):
                    self.result.urls.append(url["expanded_url"])
        if self.extract_media:
            for media in entities.get("media", []):
                if media["media_url"]:
                    self.result.urls.append(media["media_url"])

    def process_warc(self, warc_filepath):
        # Dispatch message based on type.
        harvest_type = self.message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            self.process_search_warc(warc_filepath)
        elif harvest_type == "twitter_filter":
            self._process_tweets(TwitterStreamWarcIter(warc_filepath))
        elif harvest_type == "twitter_sample":
            self._process_tweets(TwitterStreamWarcIter(warc_filepath))
        elif harvest_type == "twitter_user_timeline":
            self.process_user_timeline_warc(warc_filepath)
        else:
            raise KeyError

    def process_search_warc(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)
        query = self.message["seeds"][0]["token"]

        since_id = self.state_store.get_state(__name__, u"{}.since_id".format(query)) if incremental else None

        max_tweet_id = self._process_tweets(TwitterRestWarcIter(warc_filepath))

        # Update state store
        if incremental and max_tweet_id > since_id:
            self.state_store.set_state(__name__, u"{}.since_id".format(query), max_tweet_id)

    def process_user_timeline_warc(self, warc_filepath):
        incremental = self.message.get("options", {}).get("incremental", False)

        for count, status in enumerate(TwitterRestWarcIter(warc_filepath)):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet:
                user_id = tweet["user"]["id_str"]
                if incremental:
                    # Update state
                    key = "timeline.{}.since_id".format(user_id)
                    self.state_store.set_state(__name__, key,
                                               max(self.state_store.get_state(__name__, key), tweet.get("id")))
                self._process_tweet(tweet)

    def _process_tweets(self, warc_iter):
        max_tweet_id = None
        for count, status in enumerate(warc_iter):
            tweet = status.item
            if not count % 100:
                log.debug("Processing %s tweets", count)
            if "text" in tweet:
                max_tweet_id = max(max_tweet_id, tweet.get("id"))
                self._process_tweet(tweet)
        return max_tweet_id

    def _process_tweet(self, tweet):
        self.result.increment_stats("tweets")
        # For more info, see https://dev.twitter.com/overview/api/entities-in-twitter-objects
        statuses = [tweet]
        if "retweeted_status" in tweet:
            statuses.append(tweet["retweeted_status"])
        elif "quoted_status" in tweet:
            statuses.append(tweet["quoted_status"])
        for status in statuses:
            self._process_entities(status.get("entities", {}))
            self._process_entities(status.get("extended_entities", {}))
        if self.extract_user_profile_images:
            self.result.urls.append(tweet["user"]["profile_image_url"])
            self.result.urls.append(tweet["user"]["profile_background_image_url"])
            if "profile_banner_url" in tweet["user"]:
                self.result.urls.append(tweet["user"]["profile_banner_url"])


if __name__ == "__main__":
    TwitterHarvester.main(TwitterHarvester, QUEUE, [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
