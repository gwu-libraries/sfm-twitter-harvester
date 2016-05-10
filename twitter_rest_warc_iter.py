#!/usr/bin/env python

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter
from dateutil.parser import parse as date_parse

SEARCH_URL = "https://api.twitter.com/1.1/search/tweets.json"
TIMELINE_URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"


class TwitterRestWarcIter(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        return url.startswith(SEARCH_URL) or url.startswith(TIMELINE_URL)

    def _item_iter(self, url, json_obj):
        # Search has { "statuses": [tweets] }
        # Timeline has [tweets]
        tweet_list = json_obj["statuses"] if url.startswith(SEARCH_URL) else json_obj
        for status in tweet_list:
            yield "twitter_status", status["id_str"], date_parse(status["created_at"]), status

    @staticmethod
    def item_types():
        return ["twitter_status"]

    def _select_item(self, item):
        if not self.limit_user_ids or item.get("user", {}).get("id_str") in self.limit_user_ids:
            return True
        return False

if __name__ == "__main__":
    TwitterRestWarcIter.main(TwitterRestWarcIter)
