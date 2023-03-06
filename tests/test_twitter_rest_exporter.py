#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import tests
from tests.tweets import tweet2
#from twitter_rest_exporter import TwitterRestStatusTable
from twitter_rest_exporter import BaseTwitterStatusTable, BaseTwitterTwoStatusTable, TwitterRestExporter2
from twitter_rest_warc_iter import TwitterRestWarcIter2
from datetime import datetime
import os
import tempfile
import shutil
import json
from mock import MagicMock, patch, Mock, PropertyMock
from sfmutils.exporter import BaseTable, BaseExporter, CODE_WARC_MISSING, CODE_NO_WARCS, CODE_BAD_REQUEST
from sfmutils.api_client import ApiClient
from sfmutils.warc_iter import IterItem
from sfmutils.utils import datetime_now
import iso8601

from kombu import Producer, Connection, Exchange

class TestTwitterStatusTable(tests.TestCase):
    def test_row(self):
        table_cls = create_twitter_status_table_class(BaseTwitterStatusTable)
        table = table_cls(None, None, None, None, None, None)
        row = table._row(tweet2)
        self.assertEqual("660065173563158529", row[0])
        self.assertEqual("https://twitter.com/justin_littman/status/660065173563158529", row[1])
        self.assertIsInstance(row[3], datetime)
        self.assertEqual("justin_littman", row[4])
        self.assertEqual("My new blog post on techniques for harvesting social media to WARCs: https://t.co/OHZki6pXEe",
                         row[5])
        self.assertEqual("original", row[6])

class TestTwitterRestExporter2(tests.TestCase):
    '''
    Replicating tests from sfm-utils/tests/sfm-utils/test_exporter.py. The rest exporter for Twitter v2. overrides BaseExporter.on_message(), so we want to test the overridden functionality.
    '''
    def setUp(self):
        self.warc_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warcs")
        self.warcs = [{"warc_id": '98f80e8e86c64e99b72efb04adec6e19',
                    "path": "3f31860b31a34935b5a3c03b97baced8-20230303160142076-00000-lan28ikm.warc.gz",
                    "sha1": "c50876a4e5e6b33b93e8c8abfc4727c43fc28344",
                    "bytes": "7605",
                    "date_created": "2023-03-03T16:01:43Z"},
                    {"warc_id": '14c88b40c2a8485383809245f740119f',
                    "path": "0d306636fa5a449db529726a050eae32-20230303155805784-00000-obwhr8ac.warc.gz",
                    "sha1": "8d50088944f9ab25042a61d1c14b5af918202854",
                    "bytes": "2869",
                    "date_created": "2023-03-03T15:58:07Z"}]
        self.warc_filepaths = [
            os.path.join(self.warc_base_path, self.warcs[0]['path']),
            os.path.join(self.warc_base_path, self.warcs[1]['path'])
        ]
        self.export_path = tempfile.mkdtemp()
        self.working_path = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.export_path):
            shutil.rmtree(self.export_path)
        if os.path.exists(self.working_path):
            shutil.rmtree(self.working_path)
    

    def test_export_csv(self):
        self.export_collection(export_format='csv')
        csv_filepath = os.path.join(self.export_path, "test1_001.csv")
        self.assertTrue(os.path.exists(csv_filepath))
        with open(csv_filepath, "r") as f:
            lines = f.readlines()
            self.assertEqual(10, len(lines))

    
    def test_export_full_json(self):
        self.export_collection(export_format='json_full')
        

    @patch("sfmutils.exporter.ApiClient", autospec=True)
    # Mock out Producer
    @patch("sfmutils.consumer.ConsumerProducerMixin.producer", new_callable=PropertyMock, spec=Producer)    
    def export_collection(self, mock_producer, mock_api_client_cls, export_format):
        '''
        Testing the export on a collection (CSV or full JSON)
        '''
        mock_api_client = MagicMock(spec=ApiClient)
        mock_api_client_cls.side_effect = [mock_api_client]
        mock_api_client.warcs.side_effect = [self.warcs]

        mock_connection = MagicMock(spec=Connection)
        mock_exchange = MagicMock(spec=Exchange)
        mock_exchange.name = "test exchange"

        item_date_start = "2023-01-25T12:00:00Z"
        item_datetime_start = iso8601.parse_date(item_date_start)
        item_date_end = "2023-03-03T15:58:00Z"
        item_datetime_end = iso8601.parse_date(item_date_end)
        harvest_date_start = "2023-03-03T15:58:00Z"
        harvest_date_end = "2023-03-03T16:05:00Z"

        export_message = {
            "id": "test1",
            "type": "test_search2",
            "collection": {
                "id": "eeb80f0540fd4a978bf414bf0084a010"
            },
            "format": export_format,
            "segment_size": None,
            "path": self.export_path,
            "dedupe": True,
            "item_date_start": item_date_start,
            "item_date_end": item_date_end,
            "harvest_date_start": harvest_date_start,
            "harvest_date_end": harvest_date_end,

        }

        exporter = TwitterRestExporter2("http://test", self.working_path,  warc_base_path=self.warc_base_path)

        exporter.mq_config = True
        exporter._producer_connection = mock_connection
        exporter.exchange = mock_exchange

        exporter.routing_key = "export.start.test.test_search2"
        exporter.message = export_message
        exporter.on_message()

        mock_api_client_cls.assert_called_once_with("http://test")
        mock_api_client.warcs.assert_called_once_with(collection_id="eeb80f0540fd4a978bf414bf0084a010",
                                                      seed_ids=[], harvest_date_start=harvest_date_start,
                                                      harvest_date_end=harvest_date_end)

        self.assertTrue(exporter.result.success)

        # We skip the rests of the test, since the functionality is the same as in BaseExporter

   