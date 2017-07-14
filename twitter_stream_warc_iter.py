#!/usr/bin/env python

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter
from dateutil.parser import parse as date_parse
from twitter_rest_warc_iter import twitter_row
import json
import sys


class TwitterStreamWarcIter(BaseWarcIter):
    def __init__(self, filepaths, limit_user_ids=None):
        BaseWarcIter.__init__(self, filepaths)
        self.limit_user_ids = limit_user_ids

    def _select_record(self, url):
        return url.startswith("https://stream.twitter.com/1.1")

    def _item_iter(self, url, json_obj):
        # Only want statuses, not deletes, stall_warnings, etc.
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

    def print_elk_warc_iter(self, pretty=False, fp=sys.stdout, limit_item_types=None, print_item_type=False,
                            dedupe=True):
        # if necessary, put it into the base class implementation
        for item_type, _, _, _, item in self.iter(limit_item_types=limit_item_types, dedupe=dedupe):
            if print_item_type:
                fp.write("{}:".format(item_type))
            json.dump(twitter_row(item), fp, indent=4 if pretty else None)
            fp.write("\n")

    def print_elk_json_iter(self, pretty=False, fp=sys.stdout):
        for filepath in self.filepaths:
            with open(filepath, 'r') as f:
                for line in f:
                    json.dump(twitter_row(json.loads(line)), fp, indent=4 if pretty else None)
                    fp.write("\n")

if __name__ == "__main__":
    TwitterStreamWarcIter.main(TwitterStreamWarcIter)
