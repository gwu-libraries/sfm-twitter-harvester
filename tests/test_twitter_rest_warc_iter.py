from __future__ import absolute_import
import tests
from twitter_rest_warc_iter import TwitterRestWarcIter


class TestTwitterRestWarcIter(tests.TestCase):
    def setUp(self):
        self.filepaths = ("tests/warcs/0f81e11d83494d73aef11a7ce0058438-20160416155600459-00000-71-66c4024617a3-"
                          "8000.warc.gz",
                          "tests/warcs/test_1-20151202190229530-00000-29525-GLSS-F0G5RP-8000.warc.gz")

    def test_no_limit(self):
        warc_iter = TwitterRestWarcIter(self.filepaths)
        tweets = list(warc_iter)
        self.assertEqual(1473, len(tweets))
        self.assertEqual("721345764362948609", tweets[0][1])
        # Datetime is aware
        self.assertIsNotNone(tweets[0][2].tzinfo)

    def test_limit(self):
        warc_iter = TwitterRestWarcIter(self.filepaths, limit_user_ids=("481186914", "999999"))
        self.assertEqual(244, len(list(warc_iter)))

        warc_iter = TwitterRestWarcIter(self.filepaths, limit_user_ids=("999999",))
        self.assertEqual(0, len(list(warc_iter)))

    def test_ignore_errors(self):
        self.assertEqual(0, len(list(TwitterRestWarcIter._item_iter(None,
                                                                     'https://api.twitter.com/1.1/statuses/'
                                                                     'user_timeline.json',
                                                                     {'errors': [
                                                                         {'message': 'Rate limit exceeded',
                                                                          'code': 88}]}))))

        self.assertEqual(0, len(list(TwitterRestWarcIter._item_iter(None,
                                                                     'https://api.twitter.com/1.1/statuses/'
                                                                     'user_timeline.json',
                                                                     {'request': '/1.1/statuses/user_timeline.json',
                                                                         'error': 'Not authorized.'}))))
