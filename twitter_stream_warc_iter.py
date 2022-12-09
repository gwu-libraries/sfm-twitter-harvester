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


class TwitterStreamWarcIter2(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids                                    #fixed

    def _select_record(self, url):
        return url.startswith("https://api.twitter.com/2")  

    def _item_iter(self, url, json_obj):
        '''
        Flattens a list of Tweets and iterates over the list, yielding each Tweet to sfm-utils.warc_iter.BaseWarcIter.iter()
        '''
        tweet_list = ensure_flattened(json_obj)

        for tweet in tweet_list:
            # TO DO: Test if this condition works to yield only the records with content
            if "text" in tweet:
                yield "twitter_status", tweet["id"], date_parse(tweet["created_at"]), tweet    
            else:
                yield None, None, None, tweet

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


# TO DO: Need a way to invoke either 1 or 2, depending on the case 
# Consider implementing with command-line args
if __name__ == "__main__":
    TwitterStreamWarcIter2.main(TwitterStreamWarcIter2)         
