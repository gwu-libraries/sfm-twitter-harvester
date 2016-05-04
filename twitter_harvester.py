#!/usr/bin/env python

from __future__ import absolute_import
import logging
from twarc import Twarc
from sfmutils.harvester import BaseHarvester, Msg, CODE_TOKEN_NOT_FOUND

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_harvester"
SEARCH_ROUTING_KEY = "harvest.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "harvest.start.twitter.twitter_user_timeline"


class TwitterHarvester(BaseHarvester):
    def __init__(self, stream_restart_interval_secs=30 * 60, mq_config=None, debug=False):
        BaseHarvester.__init__(self, mq_config=mq_config, stream_restart_interval_secs=stream_restart_interval_secs,
                               debug=debug)
        self.twarc = None
        self.extract_media = False
        self.extract_web_resources = False

    def harvest_seeds(self):
        # Create a twarc
        self._create_twarc()

        # Get harvest extract options.
        self.extract_media = self.message.get("options", {}).get("media", False)
        self.extract_web_resources = self.message.get("options", {}).get("web_resources", False)

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
                           self.message["credentials"]["access_token_secret"])

    def search(self):
        incremental = self.message.get("options", {}).get("incremental", False)

        for seed in self.message.get("seeds", []):
            query = seed.get("token")
            # Get since_id from state_store
            since_id = self.state_store.get_state(__name__, u"{}.since_id".format(query)) if incremental else None

            max_tweet_id = self._process_tweets(self.twarc.search(query, since_id=since_id))
            log.debug("Searching on %s since %s returned %s tweets.", query,
                      since_id, self.harvest_result.summary.get("tweet"))

            # Update state store
            if incremental and max_tweet_id:
                self.state_store.set_state(__name__, u"{}.since_id".format(query), max_tweet_id)

    def filter(self):
        assert len(self.message.get("seeds", [])) == 1

        track = self.message["seeds"][0]["token"].get("track")
        follow = self.message["seeds"][0]["token"].get("follow")
        locations = self.message["seeds"][0]["token"].get("locations")

        self._process_tweets(self.twarc.filter(track=track, follow=follow, locations=locations))

    def sample(self):
        self._process_tweets(self.twarc.sample())

    def user_timeline(self):
        incremental = self.message.get("options", {}).get("incremental", False)

        for seed in self.message.get("seeds", []):
            seed_id = seed["id"]
            screen_name = seed.get("token")
            user_id = seed.get("uid")
            assert screen_name or user_id

            # If there is not a user_id, look it up.
            if screen_name and not user_id:
                user_id = self._lookup_user_id(screen_name)
                if user_id:
                    # Report back if nsid found
                    self.harvest_result.uids[seed_id] = user_id
                else:
                    msg = "User id not found for user {}".format(screen_name)
                    log.exception(msg)
                    self.harvest_result.warnings.append(Msg(CODE_TOKEN_NOT_FOUND, msg))
                    return
            # Otherwise, get the current screen_name
            else:
                new_screen_name = self._lookup_screen_name(user_id)
                if new_screen_name != screen_name:
                    self.harvest_result.token_updates[seed_id] = new_screen_name

            # Get since_id from state_store
            since_id = self.state_store.get_state(__name__,
                                                  "timeline.{}.since_id".format(user_id)) if incremental else None

            max_tweet_id = self._process_tweets(self.twarc.timeline(user_id=user_id, since_id=since_id))
            log.debug("Timeline for %s since %s returned %s tweets.", user_id,
                      since_id, self.harvest_result.summary.get("tweet"))

            # Update state store
            log.info("IS INCREMENTAL: %s", incremental)
            if incremental and max_tweet_id:
                self.state_store.set_state(__name__, "timeline.{}.since_id".format(user_id), max_tweet_id)

    def _lookup_screen_name(self, user_id):
        """
        Lookup a screen name given a user id.
        """
        users = list(self.twarc.user_lookup(user_ids=(user_id,)))
        assert len(users) in (0, 1)
        if users:
            return users[0]["screen_name"]
        return None

    def _lookup_user_id(self, screen_name):
        """
        Lookup a user id given a screen name.
        """
        users = list(self.twarc.user_lookup(screen_names=(screen_name,)))
        assert len(users) in (0, 1)
        if users:
            return users[0]["id_str"]
        return None

    def _process_tweets(self, tweets):
        max_tweet_id = None
        for count, tweet in enumerate(tweets):
            if not count % 100:
                log.debug("Processed %s tweets", count)
            if self.stop_event.is_set():
                log.debug("Stopping since stop event set.")
                break
            if "text" in tweet:
                max_tweet_id = max(max_tweet_id, tweet.get("id"))
                self.harvest_result.increment_summary("tweet")
                # For more info, see https://dev.twitter.com/overview/api/entities-in-twitter-objects
                status = tweet
                if "retweeted_status" in tweet:
                    status = tweet["retweeted_status"]
                elif "quoted_status" in tweet:
                    status = tweet["quoted_status"]
                self._process_entities(status.get("entities", {}))
                self._process_entities(status.get("extended_entities", {}))
        return max_tweet_id

    def _process_entities(self, entities):
        if self.extract_web_resources:
            for url in entities.get("urls", []):
                self.harvest_result.urls.append(url["expanded_url"])
        if self.extract_media:
            for media in entities.get("media", []):
                self.harvest_result.urls.append(media["media_url"])

if __name__ == "__main__":
    TwitterHarvester.main(TwitterHarvester, QUEUE, [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
