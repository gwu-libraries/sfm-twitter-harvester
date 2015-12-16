#!/usr/bin/env python

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter


class TwitterStreamWarcIter(BaseWarcIter):
    def _select_record(self, url):
        return url.startswith("https://stream.twitter.com/1.1")

    def _item_iter(self, url, json_obj):
        yield "twitter_status", json_obj

    @staticmethod
    def item_types():
        return ["twitter_status"]

    @property
    def line_oriented(self):
        return True

if __name__ == "__main__":
    TwitterStreamWarcIter.main(TwitterStreamWarcIter)
