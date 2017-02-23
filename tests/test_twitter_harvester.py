from __future__ import absolute_import
import tests
import unittest
from mock import MagicMock, patch, call
from twitter_harvester import TwitterHarvester
from twarc import Twarc
import threading
import shutil
import tempfile
import time
from datetime import datetime, date
import copy
import os
from kombu import Connection, Exchange, Queue, Producer
from tests.tweets import *
from sfmutils.state_store import DictHarvestStateStore
from sfmutils.harvester import HarvestResult, EXCHANGE, CODE_TOKEN_NOT_FOUND, CODE_TOKEN_UNAUTHORIZED, STATUS_RUNNING, \
    STATUS_SUCCESS
from sfmutils.warc_iter import IterItem
from twitter_rest_warc_iter import TwitterRestWarcIter
from requests.exceptions import HTTPError

base_search_message = {
    "id": "test:1",
    "type": "twitter_search",
    "path": "/collections/test_collection_set/collection_id",
    "seeds": [
        {
            "token": "gelman"
        }

    ],
    "credentials": {
        "consumer_key": tests.TWITTER_CONSUMER_KEY,
        "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
        "access_token": tests.TWITTER_ACCESS_TOKEN,
        "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
    },
    "options": {
        "web_resources": True,
        "media": True,
        "user_images": True,
        "tweets": True
    },
    "collection_set": {
        "id": "test_collection_set"
    }
}

base_timeline_message = {
    "id": "test:1",
    "type": "twitter_user_timeline",
    "path": "/collections/test_collection_set/collection_id",
    "seeds": [
        {
            "id": "seed_id1",
            "uid": "28101965"
        },
        {
            "id": "seed_id2",
            "token": "gelmanlibrary"
        }

    ],
    "options": {
        "web_resources": True,
        "media": True,
        "user_images": True,
        "tweets": True
    },
    "credentials": {
        "consumer_key": tests.TWITTER_CONSUMER_KEY,
        "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
        "access_token": tests.TWITTER_ACCESS_TOKEN,
        "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
    },
    "collection_set": {
        "id": "test_collection_set"
    }
}


class TestTwitterHarvester(tests.TestCase):
    def setUp(self):
        self.working_path = tempfile.mkdtemp()

        self.harvester = TwitterHarvester(self.working_path)
        self.harvester.state_store = DictHarvestStateStore()
        self.harvester.message = base_search_message
        self.harvester.result = HarvestResult()
        self.harvester.stop_harvest_seeds_event = threading.Event()

    def tearDown(self):
        if os.path.exists(self.working_path):
            shutil.rmtree(self.working_path)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_search(self, mock_twarc_class):
        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.search.side_effect = [(tweet1, tweet2)]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        self.harvester.message = base_search_message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5)
        self.assertEqual([call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        self.assertDictEqual({"tweets": 2}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_incremental_search(self, twarc_class):
        message = copy.deepcopy(base_search_message)
        message["options"]["incremental"] = True

        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.search.side_effect = [(tweet2,)]
        # Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        self.harvester.state_store.set_state("twitter_harvester", "gelman.since_id", 605726286741434400)
        self.harvester.message = message
        self.harvester.harvest_seeds()

        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                            http_errors=5, connection_errors=5)
        self.assertEqual([call("gelman", since_id=605726286741434400)],
                         mock_twarc.search.mock_calls)
        self.assertDictEqual({"tweets": 1}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_user_timeline(self, mock_twarc_class):
        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 user timelines. First returns 2 tweets. Second returns none.
        mock_twarc.timeline.side_effect = [(tweet1, tweet2), ()]
        # Expecting 2 calls to user_lookup
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "gwtweets"}], [{"id_str": "9710852"}]]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        self.harvester.message = base_timeline_message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5)
        self.assertEqual([call(user_id="28101965", since_id=None), call(user_id="9710852", since_id=None)],
                         mock_twarc.timeline.mock_calls)
        self.assertDictEqual({"tweets": 2}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_incremental_user_timeline(self, twarc_class):
        message = copy.deepcopy(base_timeline_message)
        message["options"]["incremental"] = True

        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 timelines. First returns 1 tweets. Second returns none.
        mock_twarc.timeline.side_effect = [(tweet2,), ()]
        # Expecting 2 calls to user_lookup
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "gwtweets"}], [{"id_str": "9710852"}]]
        # Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        self.harvester.message = message
        self.harvester.state_store.set_state("twitter_harvester", "timeline.28101965.since_id", 605726286741434400)
        self.harvester.harvest_seeds()

        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                            http_errors=5, connection_errors=5)
        self.assertEqual(
            [call(user_id="28101965", since_id=605726286741434400), call(user_id="9710852", since_id=None)],
            mock_twarc.timeline.mock_calls)
        self.assertDictEqual({"tweets": 1}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_user_timeline_with_missing_users(self, mock_twarc_class):
        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 calls to user_lookup, both which return nothing
        mock_twarc.user_lookup.side_effect = [[], []]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        message = copy.deepcopy(base_timeline_message)
        message["seeds"] = [
            {
                "id": "seed_id1",
                "token": "missing1"
            },
            {
                "id": "seed_id2",
                "token": "missing2"
            }

        ]
        self.harvester.message = message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5)

        self.assertEqual([call(screen_names=("missing1",)), call(screen_names=("missing2",))],
                         mock_twarc.user_lookup.mock_calls)
        self.assertEqual(2, len(self.harvester.result.warnings))
        self.assertEqual(CODE_TOKEN_NOT_FOUND, self.harvester.result.warnings[0].code)
        self.assertEqual("seed_id1", self.harvester.result.warnings[0].extras["seed_id"])

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_user_timeline_with_private_timeline(self, mock_twarc_class):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 401
        # Expecting 2 user timelines. First returns 2 tweets. Second returns a 404.
        mock_twarc.timeline.side_effect = [(tweet1, tweet2), HTTPError(response=mock_response)]
        # Expecting 2 calls to user_lookup
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "gwtweets"}], [{"id_str": "9710852"}]]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        self.harvester.message = base_timeline_message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5)
        self.assertEqual([call(user_id="28101965", since_id=None), call(user_id="9710852", since_id=None)],
                         mock_twarc.timeline.mock_calls)
        self.assertEqual(1, len(self.harvester.result.warnings))
        self.assertEqual(CODE_TOKEN_UNAUTHORIZED, self.harvester.result.warnings[0].code)
        self.assertEqual("seed_id2", self.harvester.result.warnings[0].extras["seed_id"])
        self.assertDictEqual({"tweets": 2}, self.harvester.result.harvest_counter)

    def test_lookup_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "justin_littman"}]]

        self.harvester.twarc = mock_twarc
        self.assertEqual("justin_littman", self.harvester._lookup_screen_name("481186914"))

        mock_twarc.user_lookup.assert_called_once_with(user_ids=("481186914",))

    def test_lookup_missing_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_twarc.user_lookup.side_effect = [HTTPError(response=mock_response)]

        self.harvester.twarc = mock_twarc
        self.assertIsNone(self.harvester._lookup_screen_name("481186914"))

        mock_twarc.user_lookup.assert_called_once_with(user_ids=("481186914",))

    def test_lookup_user_id(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[{"id_str": "481186914"}]]

        self.harvester.twarc = mock_twarc
        self.assertEqual("481186914", self.harvester._lookup_user_id("justin_littman"))

        mock_twarc.user_lookup.assert_called_once_with(screen_names=("justin_littman",))

    def test_lookup_missing_user_id(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_twarc.user_lookup.side_effect = [HTTPError(response=mock_response)]

        self.harvester.twarc = mock_twarc
        self.assertIsNone(self.harvester._lookup_user_id("justin_littman"))

        mock_twarc.user_lookup.assert_called_once_with(screen_names=("justin_littman",))

    @staticmethod
    def _iter_items(items):
        # This is useful for mocking out a warc iter
        iter_items = []
        for item in items:
            iter_items.append(IterItem(None, None, None, None, item))
        return iter_items

    def test_harvest_options_web(self):
        self.harvester.extract_media = False
        self.harvester.extract_web_resources = True
        self.harvester.extract_user_profile_images = False
        # This would normally be passed a warc iter.
        self.harvester._process_tweets(self._iter_items([tweet2, tweet3, tweet4, tweet5]))
        self.assertSetEqual({'http://bit.ly/1ipwd0B',  # url
                             'http://nlp.stanford.edu/IR-book/html/htmledition/the-url-frontier-1.html',  # from retweet
                             'http://bit.ly/1NoNeBF'  # from base tweet of quoted status
                             },
                            self.harvester.result.urls_as_set())

    def test_harvest_options_media(self):
        self.harvester.extract_media = True
        self.harvester.extract_web_resources = False
        self.harvester.extract_user_profile_images = False
        self.harvester._process_tweets(self._iter_items([tweet2, tweet3, tweet4, tweet5]))
        self.assertSetEqual({
            'http://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg',  # media/extended entity
            'http://pbs.twimg.com/media/Bv4ekbqIYAAcmXY.jpg',  # from quoted status
        }, self.harvester.result.urls_as_set())

    def test_harvest_options_user__images(self):
        self.harvester.extract_media = False
        self.harvester.extract_web_resources = False
        self.harvester.extract_user_profile_images = True
        self.harvester._process_tweets(self._iter_items([tweet2]))
        self.assertSetEqual({
            'http://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg',
            'http://abs.twimg.com/images/themes/theme1/bg.png'
        }, self.harvester.result.urls_as_set())

    def test_default_harvest_options(self):
        self.harvester.extract_media = False
        self.harvester.extract_web_resources = False

        self.harvester._process_tweets(self._iter_items([tweet2, tweet3, tweet4, tweet5]))
        self.assertSetEqual(set(), self.harvester.result.urls_as_set())

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_search(self, iter_class):
        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.message = base_search_message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
        self.assertEqual(0, len(self.harvester.result.urls_as_set()))
        iter_class.assert_called_once_with("test.warc.gz")
        # State updated
        self.assertEqual(None, self.harvester.state_store.get_state("twitter_harvester", "gelman.since_id"))

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_search_incremental(self, iter_class):
        message = copy.deepcopy(base_search_message)
        message["options"]["incremental"] = True

        self.harvester.extract_media = False
        self.harvester.extract_web_resources = True

        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.state_store.set_state("twitter_harvester", "gelman.since_id", 605726286741434400)
        self.harvester.message = message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, self.harvester.result.urls_as_set())
        iter_class.assert_called_once_with("test.warc.gz")
        # State updated
        self.assertEqual(660065173563158500,
                         self.harvester.state_store.get_state("twitter_harvester", "gelman.since_id"))

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_user_timeline(self, iter_class):
        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet1, tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.extract_media = False
        self.harvester.extract_web_resources = True

        self.harvester.message = base_timeline_message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 2}, self.harvester.result.stats_summary())
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, self.harvester.result.urls_as_set())
        iter_class.assert_called_once_with("test.warc.gz")
        # # Nothing added to state
        self.assertEqual(0, len(self.harvester.state_store.state))

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_incremental_user_timeline(self, iter_class):
        message = copy.deepcopy(base_timeline_message)
        message["options"]["incremental"] = True

        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.extract_media = False
        self.harvester.extract_web_resources = True

        self.harvester.message = message
        self.harvester.state_store.set_state("twitter_harvester", "timeline.481186914.since_id", 605726286741434400)
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, self.harvester.result.urls_as_set())
        iter_class.assert_called_once_with("test.warc.gz")
        # State updated
        self.assertEqual(660065173563158500,
                         self.harvester.state_store.get_state("twitter_harvester", "timeline.481186914.since_id"))


@unittest.skipIf(not tests.test_config_available, "Skipping test since test config not available.")
@unittest.skipIf(not tests.integration_env_available, "Skipping test since integration env not available.")
class TestTwitterHarvesterIntegration(tests.TestCase):
    @staticmethod
    def _create_connection():
        return Connection(hostname="mq", userid=tests.mq_username, password=tests.mq_password)

    def setUp(self):
        self.exchange = Exchange(EXCHANGE, type="topic")
        self.result_queue = Queue(name="result_queue", routing_key="harvest.status.twitter.*", exchange=self.exchange,
                                  durable=True)
        self.web_harvest_queue = Queue(name="web_harvest_queue", routing_key="harvest.start.web",
                                       exchange=self.exchange)
        self.warc_created_queue = Queue(name="warc_created_queue", routing_key="warc_created", exchange=self.exchange)
        twitter_harvester_queue = Queue(name="twitter_harvester", exchange=self.exchange)
        twitter_rest_harvester_queue = Queue(name="twitter_rest_harvester", exchange=self.exchange)
        with self._create_connection() as connection:
            self.result_queue(connection).declare()
            self.result_queue(connection).purge()
            self.web_harvest_queue(connection).declare()
            self.web_harvest_queue(connection).purge()
            self.warc_created_queue(connection).declare()
            self.warc_created_queue(connection).purge()
            # Declaring to avoid race condition with harvester starting.
            twitter_harvester_queue(connection).declare()
            twitter_harvester_queue(connection).purge()
            twitter_rest_harvester_queue(connection).declare()
            twitter_rest_harvester_queue(connection).purge()

        self.harvest_path = None

    def tearDown(self):
        if self.harvest_path:
            shutil.rmtree(self.harvest_path, ignore_errors=True)

    def test_search(self):
        self.harvest_path = "/sfm-data/collection_set/test_collection/test_1"
        harvest_msg = {
            "id": "test:1",
            "type": "twitter_search",
            "path": self.harvest_path,
            "seeds": [
                {
                    "id": "seed_id3",
                    "token": "gwu"
                }
            ],
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection_set": {
                "id": "test_collection_set"
            },
            "collection": {
                "id": "test_collection"
            },
            "options": {
                "web_resources": True,
                "media": True,
                "tweets": True
            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_search")

            status_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:1", status_msg["id"])
            # Running
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Another running message
            status_msg = self._wait_for_message(self.result_queue, connection)
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:1", result_msg["id"])
            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])

            # Web harvest message.
            web_harvest_msg = self._wait_for_message(self.web_harvest_queue, connection)
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_filter(self):
        self.harvest_path = "/sfm-data/collection_set/test_collection/test_2"
        harvest_msg = {
            "id": "test:2",
            "type": "twitter_filter",
            "path": self.harvest_path,
            "seeds": [
                {
                    "id": "seed_id4",
                    "token": {
                        "track": "trump"
                    }
                }
            ],
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection_set": {
                "id": "test_collection_set"
            },
            "collection": {
                "id": "test_collection"
            },
            "options": {
                "web_resources": True,
                "media": True,
                "tweets": True
            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_filter")

            status_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:2", status_msg["id"])
            # Running
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Wait 15 seconds
            time.sleep(15)

            # Send stop message
            harvest_stop_msg = {
                "id": "test:2",
            }
            producer.publish(harvest_stop_msg, routing_key="harvest.stop.twitter.twitter_filter")

            # Another running message
            status_msg = self._wait_for_message(self.result_queue, connection)
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:2", result_msg["id"])
            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])

            # Web harvest message.
            web_harvest_msg = self._wait_for_message(self.web_harvest_queue, connection)
            # Some seeds
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_sample(self):
        self.harvest_path = "/sfm-data/collection_set/test_collection/test_3"
        harvest_msg = {
            "id": "test:3",
            "type": "twitter_sample",
            "path": self.harvest_path,
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection_set": {
                "id": "test_collection_set"
            },
            "collection": {
                "id": "test_collection"
            },
            "options": {
                "web_resources": True,
                "media": True,
                "tweets": True
            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_sample")

            status_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:3", status_msg["id"])
            # Running
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Wait 15 seconds
            time.sleep(15)

            # Send stop message
            harvest_stop_msg = {
                "id": "test:3",
            }
            producer.publish(harvest_stop_msg, routing_key="harvest.stop.twitter.twitter_sample")

            # Another running message
            status_msg = self._wait_for_message(self.result_queue, connection)
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:3", result_msg["id"])
            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])

            # Web harvest message.
            web_harvest_msg = self._wait_for_message(self.web_harvest_queue, connection)
            # Some seeds
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_user_timeline(self):
        self.harvest_path = "/sfm-data/collection_set/test_collection/test_4"
        harvest_msg = {
            "id": "test:4",
            "type": "twitter_user_timeline",
            "path": self.harvest_path,
            "seeds": [
                # By screen name
                {
                    "id": "seed_id1",
                    "token": "socialfeedmgr"
                },
                {
                    "id": "seed_id2",
                    "uid": "2875189485"
                },
                {
                    "id": "seed_id3",
                    "token": "110_meryam"
                },
                {
                    "id": "seed_id4",
                    "token": "idkydktdk",
                    "uid": "326940537"
                },
                {
                    "id": "seed_id5",
                    "uid": "757448176630571009"
                }
            ],
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection_set": {
                "id": "test_collection_set"
            },
            "collection": {
                "id": "test_collection"
            },
            "options": {
                "web_resources": True,
                "media": True,
                "tweets": True
            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_user_timeline")

            status_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:4", status_msg["id"])
            # Running
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Another running message
            status_msg = self._wait_for_message(self.result_queue, connection)
            self.assertEqual(STATUS_RUNNING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:4", result_msg["id"])
            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])
            # 3 warnings
            self.assertEqual(3, len(result_msg["warnings"]))

            # Web harvest message.
            web_harvest_msg = self._wait_for_message(self.web_harvest_queue, connection)
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))


    def _wait_for_message(self, queue, connection):
        counter = 0
        message_obj = None
        bound_result_queue = queue(connection)
        while counter < 180 and not message_obj:
            time.sleep(.5)
            message_obj = bound_result_queue.get(no_ack=True)
            counter += 1
        self.assertIsNotNone(message_obj, "Timed out waiting for result at {}.".format(datetime.now()))
        return message_obj.payload
