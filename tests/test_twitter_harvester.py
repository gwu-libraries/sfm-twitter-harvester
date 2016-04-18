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
from datetime import datetime
from kombu import Connection, Exchange, Queue, Producer
from tests.tweets import tweet1, tweet2
from sfmutils.state_store import DictHarvestStateStore
from sfmutils.harvester import HarvestResult, EXCHANGE

base_search_message = {
    "id": "test:1",
    "type": "twitter_search",
    "seeds": [
        {
            "token": "gwu"
        },
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
    "collection": {
        "id": "test_collection",
        "path": "/collections/test_collection"
    }
}

base_timeline_message = {
    "id": "test:1",
    "type": "twitter_user_timeline",
    "seeds": [
        {
            "uid": "28101965"
        },
        {
            "token": "gelmanlibrary"
        }

    ],
    "credentials": {
        "consumer_key": tests.TWITTER_CONSUMER_KEY,
        "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
        "access_token": tests.TWITTER_ACCESS_TOKEN,
        "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
    },
    "collection": {
        "id": "test_collection",
        "path": "/collections/test_collection"
    }
}


class TestTwitterHarvester(tests.TestCase):
    @patch("twitter_harvester.Twarc", autospec=True)
    def test_search(self, mock_twarc_class):

        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 searches. First returns 2 tweets. Second returns none.
        mock_twarc.search.side_effect = [(tweet1, tweet2), ()]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester()
        harvester.state_store = DictHarvestStateStore()
        harvester.message = base_search_message
        harvester.harvest_result = HarvestResult()
        harvester.stop_event = threading.Event()
        harvester.harvest_result_lock = threading.Lock()
        harvester.harvest_seeds()

        self.assertDictEqual({"tweet": 2}, harvester.harvest_result.summary)
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, harvester.harvest_result.urls_as_set())
        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call("gwu", since_id=None), call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        # Nothing added to state
        self.assertEqual(0, len(harvester.state_store._state))

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_incremental_search(self, twarc_class):

        message = base_search_message.copy()
        message["options"] = {
            # Incremental means that will only retrieve new results.
            "incremental": True
        }

        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 searches. First returns 2 tweets. Second returns none.
        mock_twarc.search.side_effect = [(tweet2,), ()]
        # Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester()
        state_store = DictHarvestStateStore()
        state_store.set_state("twitter_harvester", "gwu.since_id", 605726286741434400)
        harvester.state_store = state_store
        harvester.message = message
        harvester.harvest_result = HarvestResult()
        harvester.stop_event = threading.Event()
        harvester.harvest_result_lock = threading.Lock()

        harvester.harvest_seeds()

        self.assertDictEqual({"tweet": 1}, harvester.harvest_result.summary)
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, harvester.harvest_result.urls_as_set())
        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call("gwu", since_id=605726286741434400), call("gelman", since_id=None)],
                         mock_twarc.search.mock_calls)
        # State updated
        self.assertEqual(660065173563158500, state_store.get_state("twitter_harvester", "gwu.since_id"))

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_user_timeline(self, mock_twarc_class):

        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 user timelines. First returns 2 tweets. Second returns none.
        mock_twarc.timeline.side_effect = [(tweet1, tweet2), ()]
        # Expecting 2 calls to user_lookup
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "gwtweets"}], [{"id_str": "9710852"}]]
        # Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester()
        harvester.state_store = DictHarvestStateStore()
        harvester.message = base_timeline_message
        harvester.harvest_result = HarvestResult()
        harvester.stop_event = threading.Event()
        harvester.harvest_result_lock = threading.Lock()
        harvester.harvest_seeds()

        self.assertDictEqual({"tweet": 2}, harvester.harvest_result.summary)
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, harvester.harvest_result.urls_as_set())
        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call(user_id="28101965", since_id=None), call(user_id="9710852", since_id=None)],
                         mock_twarc.timeline.mock_calls)
        # Nothing added to state
        self.assertEqual(0, len(harvester.state_store._state))

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_incremental_user_timeline(self, twarc_class):

        message = base_timeline_message.copy()
        message["options"] = {
            # Incremental means that will only retrieve new results.
            "incremental": True
        }

        mock_twarc = MagicMock(spec=Twarc)
        # Expecting 2 timelines. First returns 1 tweets. Second returns none.
        mock_twarc.timeline.side_effect = [(tweet2,), ()]
        # Expecting 2 calls to user_lookup
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "gwtweets"}], [{"id_str": "9710852"}]]
        # Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester()
        state_store = DictHarvestStateStore()
        state_store.set_state("twitter_harvester", "timeline.28101965.since_id", 605726286741434400)
        harvester.state_store = state_store
        harvester.message = message
        harvester.harvest_result = HarvestResult()
        harvester.stop_event = threading.Event()
        harvester.harvest_result_lock = threading.Lock()

        harvester.harvest_seeds()

        self.assertDictEqual({"tweet": 1}, harvester.harvest_result.summary)
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, harvester.harvest_result.urls_as_set())
        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual(
            [call(user_id="28101965", since_id=605726286741434400), call(user_id="9710852", since_id=None)],
            mock_twarc.timeline.mock_calls)
        # State updated
        self.assertEqual(660065173563158500, state_store.get_state("twitter_harvester", "timeline.28101965.since_id"))

    def test_lookup_screen_name(self):

        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[{"screen_name": "justin_littman"}]]

        harvester = TwitterHarvester()
        harvester.twarc = mock_twarc
        self.assertEqual("justin_littman", harvester._lookup_screen_name("481186914"))

        mock_twarc.user_lookup.assert_called_once_with(user_ids=("481186914",))

    def test_lookup_missing_screen_name(self):

        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[]]

        harvester = TwitterHarvester()
        harvester.twarc = mock_twarc
        self.assertIsNone(harvester._lookup_screen_name("481186914"))

        mock_twarc.user_lookup.assert_called_once_with(user_ids=("481186914",))

    def test_lookup_user_id(self):

        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[{"id_str": "481186914"}]]

        harvester = TwitterHarvester()
        harvester.twarc = mock_twarc
        self.assertEqual("481186914", harvester._lookup_user_id("justin_littman"))

        mock_twarc.user_lookup.assert_called_once_with(screen_names=("justin_littman",))

    def test_lookup_missing_user_id(self):

        mock_twarc = MagicMock(spec=Twarc)
        mock_twarc.user_lookup.side_effect = [[]]

        harvester = TwitterHarvester()
        harvester.twarc = mock_twarc
        self.assertIsNone(harvester._lookup_user_id("justin_littman"))

        mock_twarc.user_lookup.assert_called_once_with(screen_names=("justin_littman",))


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

        self.collection_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.collection_path, ignore_errors=True)

    def test_search(self):
        harvest_msg = {
            "id": "test:1",
            "type": "twitter_search",
            "seeds": [
                {
                    "token": "gwu"
                }
            ],
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection": {
                "id": "test_collection",
                "path": self.collection_path

            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_search")

            # Now wait for result message.
            counter = 0
            bound_result_queue = self.result_queue(connection)
            message_obj = None
            while counter < 240 and not message_obj:
                time.sleep(.5)
                message_obj = bound_result_queue.get(no_ack=True)
                counter += 1
            self.assertTrue(message_obj, "Timed out waiting for result at {}.".format(datetime.now()))
            result_msg = message_obj.payload
            # Matching ids
            self.assertEqual("test:1", result_msg["id"])
            # Success
            self.assertEqual("completed success", result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["summary"]["tweet"])

            # Web harvest message.
            bound_web_harvest_queue = self.web_harvest_queue(connection)
            message_obj = bound_web_harvest_queue.get(no_ack=True)
            # method_frame, header_frame, web_harvest_body = self.channel.basic_get(self.web_harvest_queue)
            self.assertIsNotNone(message_obj, "No web harvest message.")
            web_harvest_msg = message_obj.payload
            # Some seeds
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # Warc created message.
            # method_frame, header_frame, warc_created_body = self.channel.basic_get(self.warc_created_queue)
            bound_warc_created_queue = self.warc_created_queue(connection)
            message_obj = bound_warc_created_queue.get(no_ack=True)
            self.assertIsNotNone(message_obj, "No warc created message.")

    def test_filter(self):
        harvest_msg = {
            "id": "test:2",
            "type": "twitter_filter",
            "seeds": [
                {
                    "token": {
                        "track": "obama"
                    }
                }
            ],
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection": {
                "id": "test_collection",
                "path": self.collection_path

            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_filter")

            # Wait 30 seconds
            time.sleep(30)

            # Send stop message
            harvest_stop_msg = {
                "id": "test:2",
            }
            producer.publish(harvest_stop_msg, routing_key="harvest.stop.twitter.twitter_filter")

            # Now wait for result message.
            counter = 0
            message_obj = None
            bound_result_queue = self.result_queue(connection)
            while counter < 180 and not message_obj:
                time.sleep(.5)
                message_obj = bound_result_queue.get(no_ack=True)
                counter += 1
            self.assertIsNotNone(message_obj, "Timed out waiting for result at {}.".format(datetime.now()))
            result_msg = message_obj.payload
            # Matching ids
            self.assertEqual("test:2", result_msg["id"])
            # Success
            self.assertEqual("completed success", result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["summary"]["tweet"])

            # Web harvest message.
            bound_web_harvest_queue = self.web_harvest_queue(connection)
            message_obj = bound_web_harvest_queue.get(no_ack=True)
            self.assertIsNotNone(message_obj, "No web harvest message.")
            web_harvest_msg = message_obj.payload
            # Some seeds
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # There may or may not be a Warc created message.

    def test_sample(self):
        harvest_msg = {
            "id": "test:3",
            "type": "twitter_sample",
            "credentials": {
                "consumer_key": tests.TWITTER_CONSUMER_KEY,
                "consumer_secret": tests.TWITTER_CONSUMER_SECRET,
                "access_token": tests.TWITTER_ACCESS_TOKEN,
                "access_token_secret": tests.TWITTER_ACCESS_TOKEN_SECRET
            },
            "collection": {
                "id": "test_collection",
                "path": self.collection_path

            }
        }
        with self._create_connection() as connection:
            bound_exchange = self.exchange(connection)
            producer = Producer(connection, exchange=bound_exchange)
            producer.publish(harvest_msg, routing_key="harvest.start.twitter.twitter_sample")

            # Wait 30 seconds
            time.sleep(30)

            # Send stop message
            harvest_stop_msg = {
                "id": "test:3",
            }
            producer.publish(harvest_stop_msg, routing_key="harvest.stop.twitter.twitter_sample")

            # Now wait for result message.
            counter = 0
            message_obj = None
            bound_result_queue = self.result_queue(connection)
            while counter < 180 and not message_obj:
                time.sleep(.5)
                message_obj = bound_result_queue.get(no_ack=True)
                counter += 1
            self.assertIsNotNone(message_obj, "Timed out waiting for result at {}.".format(datetime.now()))
            result_msg = message_obj.payload
            # Matching ids
            self.assertEqual("test:3", result_msg["id"])
            # Success
            self.assertEqual("completed success", result_msg["status"])
            # Some tweets
            self.assertTrue(result_msg["summary"]["tweet"])

            # Web harvest message.
            bound_web_harvest_queue = self.web_harvest_queue(connection)
            message_obj = bound_web_harvest_queue.get(no_ack=True)
            self.assertIsNotNone(message_obj, "No web harvest message.")
            web_harvest_msg = message_obj.payload
            # Some seeds
            self.assertTrue(len(web_harvest_msg["seeds"]))

            # There may or may not be a Warc created message.
