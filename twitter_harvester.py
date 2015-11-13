from __future__ import absolute_import
import logging
from twarc import Twarc
from sfmutils.harvester import BaseHarvester


log = logging.getLogger(__name__)

QUEUE = "twitter_rest_harvester"
ROUTING_KEY = "harvest.start.twitter.twitter_search"


class TwitterHarvester(BaseHarvester):
    def __init__(self, mq_config, process_interval_secs=1200):
        BaseHarvester.__init__(self, mq_config, process_interval_secs=process_interval_secs)
        self.twarc = None

    def harvest_seeds(self):
        #Create a twarc
        self._create_twarc()

        #Dispatch message based on type.
        harvest_type = self.message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            self.search()
        elif harvest_type == "twitter_filter":
            self.filter()
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
            #Get since_id from state_store
            since_id = self.state_store.get_state(__name__, "{}.since_id".format(query)) if incremental else None

            max_tweet_id = self._process_tweets(self.twarc.search(query, since_id=since_id))
            log.debug("Searching on %s since %s returned %s tweets.", query,
                      since_id, self.harvest_result.summary.get("tweet"))

            #Update state store
            if incremental and max_tweet_id:
                self.state_store.set_state(__name__, "{}.since_id".format(query), max_tweet_id)

    def filter(self):
        assert len(self.message.get("seeds", [])) == 1

        track = self.message["seeds"][0]["token"]

        self._process_tweets(self.twarc.stream(track))

    def _process_tweets(self, tweets):
        max_tweet_id = None
        for count, tweet in enumerate(tweets):
            if not count % 100:
                log.debug("Processed %s tweets", count)
            if self.stop_event.is_set():
                log.debug("Stopping since stop event set.")
                break
            if "text" in tweet:
                with self.harvest_result_lock:
                    max_tweet_id = max(max_tweet_id, tweet.get("id"))
                    self.harvest_result.increment_summary("tweet")
                    if "urls" in tweet["entities"]:
                        for url in tweet["entities"]["urls"]:
                            self.harvest_result.urls.append(url["expanded_url"])
                    if "media" in tweet["entities"]:
                        for media in tweet["entities"]["media"]:
                            self.harvest_result.urls.append(media["media_url"])
        return max_tweet_id


if __name__ == "__main__":
    TwitterHarvester.main(TwitterHarvester, QUEUE, [ROUTING_KEY])