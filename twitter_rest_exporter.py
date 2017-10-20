from sfmutils.exporter import BaseExporter, BaseTable
from twitter_rest_warc_iter import TwitterRestWarcIter
import logging
from dateutil.parser import parse as date_parse

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_exporter"
SEARCH_ROUTING_KEY = "export.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "export.start.twitter.twitter_user_timeline"


class BaseTwitterStatusTable(BaseTable):
    """
    PETL Table for Twitter statuses.
    """

    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, warc_iter_cls, segment_row_size):
        BaseTable.__init__(self, warc_paths, dedupe, item_date_start,
                           item_date_end, seed_uids, warc_iter_cls,
                           segment_row_size)

    def _header_row(self):
        return ('created_at', 'twitter_id', 'screen_name', 'location', 'followers_count',
                'friends_count', 'favorite_count/like_count', 'retweet_count',
                'hashtags', 'mentions', 'in_reply_to_screen_name',
                'twitter_url', 'text', 'is_retweet', 'is_quote', 'coordinates',
                'url1', 'url1_expanded', 'url2', 'url2_expanded', 'media_url')

    def _row(self, item):
        row = [date_parse(item['created_at']),
               item['id_str'],
               item['user']['screen_name'],
               item['user']['location'],
               item['user']['followers_count'],
               item['user']['friends_count'],
               item['favorite_count'],
               item['retweet_count'],
               ', '.join([hashtag['text'] for hashtag in item['entities']['hashtags']]),
               ', '.join([user_mentions['screen_name'] for user_mentions in item['entities']['user_mentions']]),
               item['in_reply_to_screen_name'] or '',
               'http://twitter.com/{}/status/{}'.format(item['user']['screen_name'], item['id_str']),
               (item.get('full_text') or item.get('extended_tweet', {}).get('full_text') or item['text']).replace('\n',
                                                                                                                  ' '),
               'Yes' if 'retweeted_status' in item else 'No',
               'Yes' if 'quoted_status' in item else 'No',
               str(item['coordinates']['coordinates']) if item['coordinates'] else ''
               ]
        # only show up to two urls w/expansions
        urlslist = []
        entities = item.get('extended_tweet', {}).get('entities') or item['entities']
        for url in entities['urls'][:2]:
            urlslist += [url['url'], url['expanded_url']]
        # Padding the row if URLs do not take up all 4 columns
        row += urlslist + [''] * (4 - len(urlslist))
        if 'media' in entities:
            # Only export the first media_url (haven't yet seen tweets with >1)
            for media in entities['media'][:1]:
                row += [media['media_url']]
        else:
            row += ['']
        return row

    def id_field(self):
        return "twitter_id"


class TwitterRestStatusTable(BaseTwitterStatusTable):
    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, segment_row_size=None):
        BaseTwitterStatusTable.__init__(self, warc_paths, dedupe,
                                        item_date_start, item_date_end,
                                        seed_uids, TwitterRestWarcIter,
                                        segment_row_size)


class TwitterRestExporter(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None,
                 warc_base_path=None):
        BaseExporter.__init__(self, api_base_url, TwitterRestWarcIter,
                              TwitterRestStatusTable, working_path,
                              mq_config=mq_config,
                              warc_base_path=warc_base_path)


if __name__ == "__main__":
    TwitterRestExporter.main(TwitterRestExporter, QUEUE,
                             [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
