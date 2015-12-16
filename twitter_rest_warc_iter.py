#!/usr/bin/env python

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter


class TwitterRestWarcIter(BaseWarcIter):
    def _select_record(self, url):
        return url.startswith("https://api.twitter.com/1.1")

    def _item_iter(self, url, json_obj):
        for status in json_obj["statuses"]:
            yield "twitter_status", status

    @staticmethod
    def item_types():
        return ["twitter_status"]

if __name__ == "__main__":
    TwitterRestWarcIter.main(TwitterRestWarcIter)
