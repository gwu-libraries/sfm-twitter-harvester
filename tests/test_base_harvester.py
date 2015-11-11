from __future__ import absolute_import
import tests
from mock import MagicMock, patch
import pika
import json
import tempfile
import os
import shutil
from twitter_rest_harvester import BaseHarvester
from sfmutils.state_store import NullHarvestStateStore
from sfmutils.harvester import HarvestResult, Msg
from sfmutils.warcprox import warced


def fake_warc(path, filename):
    print os.path.join(path, filename)
    with open(os.path.join(path, filename), "w") as f:
        f.write("Fake warc")


class TestableHarvester(BaseHarvester):
    def __init__(self, state_store, warc_dir):
        BaseHarvester.__init__(self, None, None, None, "test_exchange", None, None, skip_connection=True)
        self.state_store = state_store
        self.harvest_seeds_state_store = None
        self.harvest_seeds_message = None
        self.warc_dir = warc_dir

    def harvest_seeds(self, message, state_store):
        #Write a fake warc file
        fake_warc(self.warc_dir, "test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000.warc.gz")
        #Remember these for asserting
        self.harvest_seeds_state_store = state_store
        self.harvest_seeds_message = message
        harvest_result = HarvestResult()
        harvest_result.infos.append(Msg("FAKE_CODE1", "This is my message."))
        harvest_result.warnings.append(Msg("FAKE_CODE2", "This is my warning."))
        harvest_result.errors.append(Msg("FAKE_CODE3", "This is my error."))
        harvest_result.urls.extend(("http://www.gwu.edu", "http://library.gwu.edu"))
        harvest_result.increment_summary("photo", increment=12)
        harvest_result.increment_summary("user")
        harvest_result.token_updates["131866249@N02"] = "j.littman"
        harvest_result.uids["library_of_congress"] = "671366249@N03"
        return harvest_result

    def get_state_store(self, message):
        return self.state_store


class ExceptionRaisingHarvester(BaseHarvester):
    def __init__(self):
        BaseHarvester.__init__(self, None, None, None, "test_exchange", None, None, skip_connection=True)

    def harvest_seeds(self, message, state_store):
        raise Exception("Darn!")


class TestBaseHarvester(tests.TestCase):

    #Mock out tempfile so that have control over location of warc directory.
    @patch("twitter_rest_harvester.tempfile", autospec=True)
    #Mock out warcprox.
    @patch("twitter_rest_harvester.warced", autospec=True)
    def test_consume(self, mock_warced_class, mock_tempfile):
        test_collection_path = tempfile.mkdtemp()
        #Setup
        message = {
            "id": "test:1",
            "collection": {
                "id": "test_collection",
                "path": test_collection_path
            }
        }
        mock_channel = MagicMock(spec=pika.channel.Channel)
        mock_method = MagicMock(spec=pika.frame.Method)
        mock_method.delivery_tag = 1
        mock_method.routing_key = "harvest.start.test.test_usertimeline"
        mock_state_store = MagicMock(spec=NullHarvestStateStore)
        test_warc_path = tempfile.mkdtemp()
        mock_tempfile.mkdtemp.return_value = test_warc_path
        mock_warced = MagicMock(spec=warced)
        #Return mock_twarc when instantiating a twarc.
        mock_warced_class.side_effect = [mock_warced]

        #Create harvester and invoke _callback
        harvester = TestableHarvester(mock_state_store, test_warc_path)
        harvester._callback(mock_channel, mock_method, None, json.dumps(message))

        #Test assertions
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
        self.assertEqual(mock_state_store, harvester.harvest_seeds_state_store)
        self.assertEqual(message, harvester.harvest_seeds_message)
        mock_state_store.close.assert_called_once_with()
        mock_tempfile.mkdtemp.assert_called_once_with(prefix="test_1")
        mock_warced_class.assert_called_once_with("test_1", test_warc_path)
        self.assertTrue(mock_warced.__enter__.called)
        self.assertTrue(mock_warced.__exit__.called)

        #Warc path deleted
        self.assertFalse(os.path.exists(test_warc_path))

        #Warcs moved
        self.assertTrue(os.path.exists(
            os.path.join(test_collection_path,
                         "2015/11/09/19/test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000.warc.gz")))
        shutil.rmtree(test_collection_path)

        #Web harvest
        name1, _, kwargs1 = mock_channel.mock_calls[1]
        self.assertEqual("basic_publish", name1)
        self.assertEqual("harvest.start.web", kwargs1["routing_key"])
        web_harvest_message = {
            u"id": u"TestableHarvester:test:1",
            u"parent_id": u"test:1",
            u"type": u"web",
            u"seeds": [
                {
                    u"token": u"http://www.gwu.edu"
                },
                {
                    u"token": u"http://library.gwu.edu"
                }
            ],
            u"collection": {
                u"id": u"test_collection",
                u"path": test_collection_path
            }
        }
        self.assertDictEqual(web_harvest_message, json.loads(kwargs1["body"]))

        #Warc created message
        name2, _, kwargs2 = mock_channel.mock_calls[2]
        self.assertEqual("basic_publish", name2)
        self.assertEqual("test_exchange", kwargs2["exchange"])
        self.assertEqual("warc_created", kwargs2["routing_key"])
        warc_created_message = json.loads(kwargs2["body"])
        self.assertEqual(warc_created_message["collection"]["id"], "test_collection")
        self.assertEqual(warc_created_message["collection"]["path"], test_collection_path)
        self.assertEqual(warc_created_message["warc"]["path"],
                         os.path.join(test_collection_path,
                                      "2015/11/09/19/test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000.warc.gz"))
        self.assertEqual(warc_created_message["warc"]["sha1"], "3d63d3c46d5dfac8495621c9c697e2089e5359b2")
        self.assertEqual(warc_created_message["warc"]["bytes"], 9)
        self.assertEqual(warc_created_message["warc"]["id"], "test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000")
        self.assertIsNotNone(warc_created_message["warc"]["date_created"])

        #Harvest result message
        name3, _, kwargs3 = mock_channel.mock_calls[3]
        self.assertEqual("basic_publish", name3)
        self.assertEqual("test_exchange", kwargs3["exchange"])
        self.assertEqual("harvest.status.test.test_usertimeline", kwargs3["routing_key"])
        harvest_result_message = json.loads(kwargs3["body"])
        self.assertEqual(harvest_result_message["id"], "test:1")
        self.assertEqual(harvest_result_message["status"], "completed success")
        self.assertEqual(1, len(harvest_result_message["infos"]))
        self.assertDictEqual({
            "code": "FAKE_CODE1",
            "message": "This is my message."
        }, harvest_result_message["infos"][0])
        self.assertEqual(1, len(harvest_result_message["warnings"]))
        self.assertDictEqual({
            "code": "FAKE_CODE2",
            "message": "This is my warning."
        }, harvest_result_message["warnings"][0])
        self.assertEqual(1, len(harvest_result_message["errors"]))
        self.assertDictEqual({
            "code": "FAKE_CODE3",
            "message": "This is my error."
        }, harvest_result_message["errors"][0])
        self.assertIsNotNone(harvest_result_message["date_started"])
        self.assertIsNotNone(harvest_result_message["date_ended"])
        self.assertDictEqual({
            "photo": 12,
            "user": 1
        }, harvest_result_message["summary"])
        self.assertDictEqual({
            "131866249@N02": "j.littman"
        }, harvest_result_message["token_updates"])
        self.assertDictEqual({
            "library_of_congress": "671366249@N03"
        }, harvest_result_message["uids"])

    #Mock out tempfile so that have control over location of warc directory.
    @patch("twitter_rest_harvester.tempfile", autospec=True)
    #Mock out warcprox.
    @patch("twitter_rest_harvester.warced", autospec=True)
    def test_consume_with_exception(self, mock_warced_class, mock_tempfile):
        test_collection_path = tempfile.mkdtemp()
        #Setup
        message = {
            "id": "test:1",
            "collection": {
                "id": "test_collection",
                "path": test_collection_path
            }
        }
        mock_channel = MagicMock(spec=pika.channel.Channel)
        mock_method = MagicMock(spec=pika.frame.Method)
        mock_method.delivery_tag = 1
        mock_method.routing_key = "harvest.start.test.test_usertimeline"
        test_warc_path = tempfile.mkdtemp()
        mock_tempfile.mkdtemp.return_value = test_warc_path
        mock_warced = MagicMock(spec=warced)
        #Return mock_twarc when instantiating a twarc.
        mock_warced_class.side_effect = [mock_warced]

        #Create harvester and invoke _callback
        harvester = ExceptionRaisingHarvester()
        harvester._callback(mock_channel, mock_method, None, json.dumps(message))

        #Test assertions
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
        mock_tempfile.mkdtemp.assert_called_once_with(prefix="test_1")
        mock_warced_class.assert_called_once_with("test_1", test_warc_path)
        self.assertTrue(mock_warced.__enter__.called)
        self.assertTrue(mock_warced.__exit__.called)

        #Warc path deleted
        self.assertFalse(os.path.exists(test_warc_path))

        #Harvest result message
        name1, _, kwargs1 = mock_channel.mock_calls[1]
        self.assertEqual("basic_publish", name1)
        self.assertEqual("test_exchange", kwargs1["exchange"])
        self.assertEqual("harvest.status.test.test_usertimeline", kwargs1["routing_key"])
        harvest_result_message = json.loads(kwargs1["body"])
        self.assertEqual(harvest_result_message["id"], "test:1")
        self.assertEqual(harvest_result_message["status"], "completed failure")
        self.assertEqual(1, len(harvest_result_message["errors"]))
        self.assertDictEqual({
            "code": "unknown_error",
            "message": "Darn!"
        }, harvest_result_message["errors"][0])

    def test_list_warcs(self):
        harvester = BaseHarvester(None, None, None, None, None, None, skip_connection=True)
        warc_dir = tempfile.mkdtemp()
        fake_warc(warc_dir, "test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000.warc.gz")
        fake_warc(warc_dir, "test_1-20151109195229879-00001-97528-GLSS-F0G5RP-8000.warc")
        fake_warc(warc_dir, "test_1-20151109195229879-00002-97528-GLSS-F0G5RP-8000")
        os.mkdir(os.path.join(warc_dir, "test_1-20151109195229879-00003-97528-GLSS-F0G5RP-8000.warc.gz"))
        try:
            warc_dirs = harvester._list_warcs(warc_dir)
            self.assertSetEqual({"test_1-20151109195229879-00000-97528-GLSS-F0G5RP-8000.warc.gz",
                                 "test_1-20151109195229879-00001-97528-GLSS-F0G5RP-8000.warc"},
                                set(warc_dirs))
        finally:
            shutil.rmtree(warc_dir)