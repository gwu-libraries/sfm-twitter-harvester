from __future__ import absolute_import
import tests
import unittest
from mock import MagicMock, patch, call
from twitter_harvester import TwitterHarvester
from twarc import Twarc
import threading
import pika
import shutil
import tempfile
import json
import time
from tests.tweets import tweet1, tweet2
from sfmutils.state_store import DictHarvestStateStore
from sfmutils.harvester import HarvestResult, MqConfig, EXCHANGE

base_message = {
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


class TestTwitterHarvester(tests.TestCase):
    @patch("twitter_harvester.Twarc", autospec=True)
    def test_search(self, mock_twarc_class):

        mock_twarc = MagicMock(spec=Twarc)
        #Expecting 2 searches. First returns 2 tweets. Second returns none.
        mock_twarc.search.side_effect = [(tweet1, tweet2), ()]
        #Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester(MqConfig(None, None, None, None, None, skip_connection=True))
        harvester.state_store = DictHarvestStateStore()
        harvester.message = base_message
        harvester.harvest_result = HarvestResult()
        harvester.stop_event = threading.Event()
        harvester.harvest_result_lock = threading.Lock()
        harvester.harvest_seeds()

        self.assertDictEqual({"tweet": 2}, harvester.harvest_result.summary)
        self.assertSetEqual({"http://bit.ly/1ipwd0B"}, harvester.harvest_result.urls_as_set())
        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                                 tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call("gwu", since_id=None), call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        #Nothing added to state
        self.assertEqual(0, len(harvester.state_store._state))

    @patch("twitter_harvester.Twarc", autospec=True)
    def test_incremental_search(self, twarc_class):

        message = base_message.copy()
        message["options"] = {
            #Incremental means that will only retrieve new results.
            "incremental": True
        }

        mock_twarc = MagicMock(spec=Twarc)
        #Expecting 2 searches. First returns 2 tweets. Second returns none.
        mock_twarc.search.side_effect = [(tweet2,), ()]
        #Return mock_twarc when instantiating a twarc.
        twarc_class.side_effect = [mock_twarc]

        harvester = TwitterHarvester(MqConfig(None, None, None, None, None, skip_connection=True))
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
        self.assertEqual([call("gwu", since_id=605726286741434400), call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        #State updated
        self.assertEqual(660065173563158500, state_store.get_state("twitter_harvester", "gwu.since_id"))

@unittest.skipIf(not tests.test_config_available, "Skipping test since test config not available.")
@unittest.skipIf(not tests.integration_env_available, "Skipping test since integration env not available.")
class TestTwitterHarvesterIntegration(tests.TestCase):
    def setUp(self):
        credentials = pika.PlainCredentials(tests.mq_username, tests.mq_password)
        parameters = pika.ConnectionParameters(host="mq", credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        #Declare result queue
        result = self.channel.queue_declare(exclusive=True)
        self.result_queue = result.method.queue
        #Bind
        self.channel.queue_bind(exchange=EXCHANGE,
                                queue=self.result_queue, routing_key="harvest.status.twitter.*")
        #Declare web harvest queue
        result = self.channel.queue_declare(exclusive=True)
        self.web_harvest_queue = result.method.queue
        #Bind
        self.channel.queue_bind(exchange=EXCHANGE,
                                queue=self.web_harvest_queue, routing_key="harvest.start.web")
        #Declare warc_created queue
        result = self.channel.queue_declare(exclusive=True)
        self.warc_created_queue = result.method.queue
        #Bind
        self.channel.queue_bind(exchange=EXCHANGE,
                                queue=self.warc_created_queue, routing_key="warc_created")

        self.collection_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.collection_path, ignore_errors=True)
        self.channel.close()
        self.connection.close()

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
        self.channel.basic_publish(exchange=EXCHANGE,
                                   routing_key="harvest.start.twitter.twitter_search",
                                   properties=pika.spec.BasicProperties(content_type="application/json",
                                                                        delivery_mode=2),
                                   body=json.dumps(harvest_msg, indent=4))

        #Now wait for result message.
        result_body = None
        counter = 0
        while counter < 180:
            time.sleep(.5)
            method_frame, header_frame, result_body = self.channel.basic_get(self.result_queue)
            if result_body:
                self.channel.basic_ack(method_frame.delivery_tag)
                break
            counter += 1
        self.assertTrue(result_body, "Timed out waiting for result.")
        result_msg = json.loads(result_body)
        #Matching ids
        self.assertEqual("test:1", result_msg["id"])
        #Success
        self.assertEqual("completed success", result_msg["status"])
        #Some tweets
        self.assertTrue(result_msg["summary"]["tweet"])

        #Web harvest message.
        method_frame, header_frame, web_harvest_body = self.channel.basic_get(self.web_harvest_queue)
        self.assertTrue(web_harvest_body, "No web harvest message.")
        web_harvest_msg = json.loads(web_harvest_body)
        #Some seeds
        self.assertTrue(len(web_harvest_msg["seeds"]))

        #Warc created message.
        method_frame, header_frame, warc_created_body = self.channel.basic_get(self.warc_created_queue)
        self.assertTrue(web_harvest_body, "No warc created message.")

    def test_filter(self):
        harvest_msg = {
            "id": "test:2",
            "type": "twitter_filter",
            "seeds": [
                {
                    "token": "obama"
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
        self.channel.basic_publish(exchange=EXCHANGE,
                                   routing_key="harvest.start.twitter.twitter_filter",
                                   properties=pika.spec.BasicProperties(content_type="application/json",
                                                                        delivery_mode=2),
                                   body=json.dumps(harvest_msg, indent=4))

        #Wait 30 seconds
        time.sleep(30)

        #Send stop message
        harvest_stop_msg = {
            "id": "test:2",
        }
        self.channel.basic_publish(exchange=EXCHANGE,
                                   routing_key="harvest.stop.twitter.twitter_filter",
                                   properties=pika.spec.BasicProperties(content_type="application/json",
                                                                        delivery_mode=2),
                                   body=json.dumps(harvest_msg, indent=4))

        #Now wait for result message.
        result_body = None
        counter = 0
        while counter < 180:
            time.sleep(.5)
            method_frame, header_frame, result_body = self.channel.basic_get(self.result_queue)
            if result_body:
                self.channel.basic_ack(method_frame.delivery_tag)
                break
            counter += 1
        self.assertTrue(result_body, "Timed out waiting for result.")
        result_msg = json.loads(result_body)
        #Matching ids
        self.assertEqual("test:2", result_msg["id"])
        #Success
        self.assertEqual("completed success", result_msg["status"])
        #Some tweets
        self.assertTrue(result_msg["summary"]["tweet"])

        #Web harvest message.
        method_frame, header_frame, web_harvest_body = self.channel.basic_get(self.web_harvest_queue)
        self.assertTrue(web_harvest_body, "No web harvest message.")
        web_harvest_msg = json.loads(web_harvest_body)
        #Some seeds
        self.assertTrue(len(web_harvest_msg["seeds"]))

        #Warc created message.
        method_frame, header_frame, warc_created_body = self.channel.basic_get(self.warc_created_queue)
        self.assertTrue(web_harvest_body, "No warc created message.")
