#!/usr/bin/env python3

from __future__ import absolute_import
import re
from sfmutils.warc_iter import BaseWarcIter
from dateutil.parser import parse as date_parse
import json
import sys

from twarc.expansions import ensure_flattened

SEARCH_URL = "https://api.twitter.com/1.1/search/tweets.json"
TIMELINE_URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"
SEARCH_URL_2 = re.compile(r"https://api.twitter.com/2/tweets/(?:search/(?:recent|all)|sample/stream)")
TIMELINE_URL_2 = re.compile(r"https://api.twitter.com/2/users/[^/]+/(?:tweets|mentions)")
API_V1 = "https://api.twitter.com/1.1/"
API_V2 = "https://api.twitter.com/2/"

class TwitterRestWarcIter(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        return url.startswith(SEARCH_URL) or url.startswith(TIMELINE_URL)

    def _item_iter(self, url, json_obj):
        return TwitterRestWarcIter._get_iter(url, json_obj)

    @staticmethod
    def _get_iter(url, json_obj):
        # Ignore error messages
        if isinstance(json_obj, dict) and ('error' in json_obj or 'errors' in json_obj):
            return
        # Search has { "statuses": [tweets] }
        # Timeline has [tweets]
        tweet_list = json_obj.get("statuses", []) if url.startswith(SEARCH_URL) else json_obj
        for status in tweet_list:
            yield "twitter_status", status["id_str"], date_parse(status["created_at"]), status

    @staticmethod
    def item_types():
        return ["twitter_status"]

    def _select_item(self, item):
        if not self.limit_user_ids or item.get("user", {}).get("id_str") in self.limit_user_ids:
            return True
        return False


class TwitterRestWarcIter2(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        return SEARCH_URL_2.match(url) or TIMELINE_URL_2.match(url)

    def _item_iter(self, url, json_obj):
        return TwitterRestWarcIter2._get_iter(url, json_obj)

    @staticmethod
    def _get_iter(url, json_obj):
        # Ignore error messages
        if not isinstance(json_obj, dict) or not 'data' in json_obj:
            return
        # Both search and timeline hold a list of tweets in "data" but need to be "flattened" to include expansions
        tweet_list = ensure_flattened(json_obj)
        for status in tweet_list:
            yield "twitter_status", status["id"], date_parse(status["created_at"]), status

    @staticmethod
    def item_types():
        return ["twitter_status"]

    def _select_item(self, item):
        if not self.limit_user_ids or item.get("author_id") in self.limit_user_ids:
            return True
        return False

class TwitterRestWarcIterAutoVersion(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        if url.startswith(API_V1):
            return url.startswith(SEARCH_URL) or url.startswith(TIMELINE_URL)
        elif url.startswith(API_V2):
            return SEARCH_URL_2.match(url) or TIMELINE_URL_2.match(url)
        return False

    def _item_iter(self, url, json_obj):
        if url.startswith(API_V1):
            return TwitterRestWarcIter._get_iter(url, json_obj)
        if url.startswith(API_V2):
            return TwitterRestWarcIter2._get_iter(url, json_obj)

    @staticmethod
    def item_types():
        return ["twitter_status"]

    def _select_item(self, item):
        if not self.limit_user_ids or item.get("user", {}).get("id_str") in self.limit_user_ids:
            return True
        return False


if __name__ == "__main__":
    TwitterRestWarcIterAutoVersion.main(TwitterRestWarcIterAutoVersion)
