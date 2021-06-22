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
from sfmutils.harvester import HarvestResult, EXCHANGE, CODE_TOKEN_NOT_FOUND, STATUS_RUNNING, \
    STATUS_SUCCESS, STATUS_STOPPING
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
                                                 http_errors=5, connection_errors=5, tweet_mode="extended")
        self.assertEqual([call("gelman", geocode=None, since_id=None)], mock_twarc.search.mock_calls)
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
                                            http_errors=5, connection_errors=5, tweet_mode="extended")
        self.assertEqual([call("gelman", geocode=None, since_id=605726286741434400)],
                         mock_twarc.search.mock_calls)
        self.assertDictEqual({"tweets": 1}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_new_search(self, mock_twarc_class):
        # The new search style has separate query and geocode parameters for search. However, the legacy
        # style is still accepted.
        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.search.side_effect = [(tweet1, tweet2)]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        search_message = copy.deepcopy(base_search_message)
        search_message["seeds"][0]["token"] = {"query": "gelman", "geocode": "38.899434,-77.036449,50mi"}

        self.harvester.message = search_message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5, tweet_mode="extended")
        self.assertEqual([call("gelman", since_id=None, geocode="38.899434,-77.036449,50mi")],
                         mock_twarc.search.mock_calls)
        self.assertDictEqual({"tweets": 2}, self.harvester.result.harvest_counter)

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_user_timeline(self, mock_twarc_class):
        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 user timelines. First returns 2 tweets. Second returns none.
        mock_twarc.timeline.side_effect = [(tweet1, tweet2), ()]
        # Expecting 2 calls to get for user lookup
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {"screen_name": "gwtweets", "protected": False}
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"id_str": "9710852", "protected": False}
        mock_twarc.get.side_effect = [mock_response1, mock_response2]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        self.harvester.message = base_timeline_message
        self.harvester.harvest_seeds()

        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                                 http_errors=5, connection_errors=5, tweet_mode="extended")
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
        # Expecting 2 calls to get for user lookup
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {"screen_name": "gwtweets", "protected": False}
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {"id_str": "9710852", "protected": False}
        mock_twarc.get.side_effect = [mock_response1, mock_response2]
        # Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        self.harvester.message = message
        self.harvester.state_store.set_state("twitter_harvester", "timeline.28101965.since_id", 605726286741434400)
        self.harvester.harvest_seeds()

        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET,
                                            http_errors=5, connection_errors=5, tweet_mode="extended")
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

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": [{"code": 50, "message": "User not found."}]}
        mock_twarc.get.side_effect = HTTPError(response=mock_response)

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
                                                 http_errors=5, connection_errors=5, tweet_mode="extended")

        self.assertEqual(
            [call('https://api.twitter.com/1.1/users/show.json', allow_404=True, params={'screen_name': 'missing1'}),
             call('https://api.twitter.com/1.1/users/show.json', allow_404=True, params={'screen_name': 'missing2'})],
            mock_twarc.get.mock_calls)
        self.assertEqual(2, len(self.harvester.result.warnings))
        self.assertEqual(CODE_TOKEN_NOT_FOUND, self.harvester.result.warnings[0].code)
        self.assertEqual("seed_id1", self.harvester.result.warnings[0].extras["seed_id"])

    def test_lookup_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"screen_name": "justin_littman", "protected": False}
        mock_twarc.get.return_value = mock_response

        self.harvester.twarc = mock_twarc
        self.assertEqual(('OK', {'protected': False, 'screen_name': 'justin_littman'}),
                         self.harvester._lookup_user(id="481186914", id_type="user_id"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'user_id': '481186914'})

    def test_lookup_protected_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"screen_name": "justin_littman", "protected": True}
        mock_twarc.get.return_value = mock_response

        self.harvester.twarc = mock_twarc
        self.assertEqual(('unauthorized', {'protected': True, 'screen_name': 'justin_littman'}),
                         self.harvester._lookup_user(id="481186914", id_type="user_id"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'user_id': '481186914'})

    def test_lookup_missing_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": [{"code": 50, "message": "User not found."}]}
        mock_twarc.get.side_effect = HTTPError(response=mock_response)

        self.harvester.twarc = mock_twarc
        self.assertEqual(('not_found', None), self.harvester._lookup_user(id="481186914", id_type="user_id"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'user_id': '481186914'})

    def test_lookup_suspended_screen_name(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"errors": [{"code": 63, "message": "User has been suspended."}]}
        mock_twarc.get.side_effect = HTTPError(response=mock_response)

        self.harvester.twarc = mock_twarc
        self.assertEqual(('suspended', None), self.harvester._lookup_user(id="481186914", id_type="user_id"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'user_id': '481186914'})

    def test_lookup_user_id(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"user_id": "481186914", "protected": False}
        mock_twarc.get.return_value = mock_response

        self.harvester.twarc = mock_twarc
        self.assertEqual(('OK', {'protected': False, 'user_id': '481186914'}),
                         self.harvester._lookup_user(id="justin_littman", id_type="screen_name"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'screen_name': 'justin_littman'})

    def test_lookup_missing_user_id(self):
        mock_twarc = MagicMock(spec=Twarc)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": [{"code": 50, "message": "User not found."}]}
        mock_twarc.get.side_effect = [HTTPError(response=mock_response)]

        self.harvester.twarc = mock_twarc
        self.assertEqual(('not_found', None), self.harvester._lookup_user(id="justin_littman", id_type="screen_name"))

        mock_twarc.get.assert_called_once_with('https://api.twitter.com/1.1/users/show.json', allow_404=True,
                                               params={'screen_name': 'justin_littman'})

    @staticmethod
    def _iter_items(items):
        # This is useful for mocking out a warc iter
        iter_items = []
        for item in items:
            iter_items.append(IterItem(None, None, None, None, item))
        return iter_items

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_search(self, iter_class):
        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.message = base_search_message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
        iter_class.assert_called_once_with("test.warc.gz")
        # State updated
        self.assertEqual(None, self.harvester.state_store.get_state("twitter_harvester", "gelman.since_id"))

    @patch("twitter_harvester.TwitterRestWarcIter", autospec=True)
    def test_process_search_incremental(self, iter_class):
        message = copy.deepcopy(base_search_message)
        message["options"]["incremental"] = True

        mock_iter = MagicMock(spec=TwitterRestWarcIter)
        mock_iter.__iter__.side_effect = [self._iter_items([tweet2]).__iter__()]
        # Return mock_iter when instantiating a TwitterRestWarcIter.
        iter_class.side_effect = [mock_iter]

        self.harvester.state_store.set_state("twitter_harvester", "gelman.since_id", 605726286741434400)
        self.harvester.message = message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
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

        self.harvester.message = base_timeline_message
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 2}, self.harvester.result.stats_summary())
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

        self.harvester.message = message
        self.harvester.state_store.set_state("twitter_harvester", "timeline.481186914.since_id", 605726286741434400)
        self.harvester.process_warc("test.warc.gz")

        self.assertDictEqual({"tweets": 1}, self.harvester.result.stats_summary())
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
        self.warc_created_queue = Queue(name="warc_created_queue", routing_key="warc_created", exchange=self.exchange)
        twitter_harvester_queue = Queue(name="twitter_harvester", exchange=self.exchange)
        twitter_rest_harvester_queue = Queue(name="twitter_rest_harvester", exchange=self.exchange)
        with self._create_connection() as connection:
            self.result_queue(connection).declare()
            self.result_queue(connection).purge()
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
        self.harvest_path = "/sfm-collection-set-data/collection_set/test_collection/test_1"
        harvest_msg = {
            "id": "test:1",
            "type": "twitter_search",
            "path": self.harvest_path,
            "seeds": [
                {
                    "id": "seed_id3",
                    "token": {
                        "query": "gelman",
                        "geocode": None
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

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_filter(self):
        self.harvest_path = "/sfm-collection-set-data/collection_set/test_collection/test_2"
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
            self.assertEqual(STATUS_STOPPING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:2", result_msg["id"])

            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_sample(self):
        self.harvest_path = "/sfm-collection-set-data/collection_set/test_collection/test_3"
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
            self.assertEqual(STATUS_STOPPING, status_msg["status"])

            # Now wait for result message.
            result_msg = self._wait_for_message(self.result_queue, connection)
            # Matching ids
            self.assertEqual("test:3", result_msg["id"])
            # Success
            self.assertEqual(STATUS_SUCCESS, result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["stats"][date.today().isoformat()]["tweets"])

            # Warc created message.
            self.assertTrue(self._wait_for_message(self.warc_created_queue, connection))

    def test_user_timeline(self):
        self.harvest_path = "/sfm-collection-set-data/collection_set/test_collection/test_4"
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
