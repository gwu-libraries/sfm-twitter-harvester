#!/usr/bin/env python

from __future__ import absolute_import
from sfmutils.warc_iter import BaseWarcIter
from dateutil.parser import parse as date_parse
import json
import sys

SEARCH_URL = "https://api.twitter.com/1.1/search/tweets.json"
TIMELINE_URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"


def twitter_row(item):
    """
    item: twitter item
    sm_type: \"tweet\", id: .id_str, user_id: .user.id_str, screen_name: .user.screen_name, " \
             "created_at: .created_at, text: (.extended_tweet.full_text // .full_text // .text), " \
             "user_mentions: [(.extended_tweet.entities // .entities).user_mentions[]?.screen_name], " \
             "hashtags: [(.extended_tweet.entities // .entities).hashtags[]?.text], " \
             "urls: [(.extended_tweet.entities // .entities).urls[]?.expanded_url]}'"
    """
    entities = item.get('extended_tweet', {}).get('entities') or item['entities']
    tweet_type = 'original'
    if item.get('in_reply_to_status_id'):
        tweet_type = 'reply'
    if 'retweeted_status' in item:
        tweet_type = 'retweet'
    if 'quoted_status' in item:
        tweet_type = 'quote'
    row = {'sm_type': 'tweet',
           'id': item['id_str'],
           'user_id': item['user']['id_str'],
           'screen_name': (item['user']['screen_name'],), 'created_at': item['created_at'],
           'text': (item.get('full_text') or
                    item.get('extended_tweet', {}).get('full_text') or
                    item['text']).replace('\n', ' '),
           'followers_count': item['user']['followers_count'],
           'friends_count': item['user']['friends_count'],
           'favorite_count': item['favorite_count'],
           'retweet_count': item['retweet_count'],
           # if the elk can't solve the insensitive case problem, just load all lower case hashtag to the elk
           'hashtags': [hashtag['text'] for hashtag in entities['hashtags']],
           'urls': [url['expanded_url'] for url in entities['urls']],
           'user_mentions': [mentions['screen_name'] for mentions in entities['user_mentions']],
           'twitter_type': tweet_type,
           'source': item['source']}

    return row


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
    TwitterRestWarcIter.main(TwitterRestWarcIter)
