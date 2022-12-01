#!/usr/bin/env python3

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter
from dateutil.parser import parse as date_parse

from twarc.expansions import ensure_flattened
from twarc import Twarc2, expansions
import json

class TwitterStreamWarcIter(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        return url.startswith("https://stream.twitter.com/1.1")

    def _item_iter(self, url, json_obj):
        # Only want statuses, not deletes, stall_warnings, etc.
        #test for stream
        #print("filter json object Adhithya Kiran",json_obj)
        if "id_str" in json_obj:
            yield "twitter_status", json_obj["id_str"], date_parse(json_obj["created_at"]), json_obj
        else:
            yield None, None, None, json_obj

    @staticmethod
    def item_types():
        return ["twitter_status"]

    @property
    def line_oriented(self):
        return True

    def _select_item(self, item):
        if not self.limit_user_ids or item.get("user", {}).get("id_str") in self.limit_user_ids:
            return True
        return False


#code for stream

class TwitterStreamWarcIter2(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids                                    #fixed

    def _select_record(self, url):
        return url.startswith("https://api.twitter.com/2")  #fixed(earlier:https://api.twitter.com/2/tweets/search/stream)

    def _item_iter(self, url, json_obj):
        # Only want statuses, not deletes, stall_warnings, etc.
        json_obj = ensure_flattened(json_obj)
        print("Adhithya Kiran json from warc_iter",json.dumps(json_obj))
        #print("json_obj Adhithya kiran",json_obj)                                                                   #ensureflattened

        if "data.id" in json_obj:
            yield "twitter_status", json_obj["data.id"], date_parse(json_obj["data.created_at"]), json_obj    #created at to data.created at
        else:
            yield None, None, None, json_obj

    @staticmethod
    def item_types():
        return ["twitter_status"]

    @property
    def line_oriented(self):
        return True

    def _select_item(self, item):                   #user to includes.users
        if not self.limit_user_ids or item.get("includes.users", {}).get("data.id") in self.limit_user_ids:
            return True
        return False



if __name__ == "__main__":
    TwitterStreamWarcIter.main(TwitterStreamWarcIter)         #RESTORED TO 1 FROM 2
