#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import tests
from tests.tweets import tweet2, tweet6, tweet7, tweet8
from twitter_rest_exporter import TwitterRestStatusTable
from datetime import datetime


class TestTwitterStatusTable(tests.TestCase):
    def test_row(self):
        table = TwitterRestStatusTable(None, None, None, None, None, None)
        row = table._row(tweet2)
        self.assertIsInstance(row[0], datetime)
        self.assertEqual("660065173563158529", row[1])
        self.assertEqual("justin_littman", row[2])
        self.assertEqual("", row[3])
        self.assertEqual(52, row[4])
        self.assertEqual(50, row[5])
        self.assertEqual(9, row[6])
        self.assertEqual(10, row[7])
        self.assertEqual("http://twitter.com/justin_littman/status/660065173563158529", row[11])
        self.assertEqual("My new blog post on techniques for harvesting social media to WARCs: https://t.co/OHZki6pXEe",
                         row[12])
        self.assertEqual("No", row[13])
        self.assertEqual("No", row[14])
        self.assertEqual("", row[15])
        self.assertEqual("https://t.co/OHZki6pXEe", row[16])
        self.assertEqual("http://bit.ly/1ipwd0B", row[17])
        self.assertEqual("", row[18])
        self.assertEqual("", row[19])
        self.assertEqual("", row[20])

    def test_stream_extended_tweet_row(self):
        table = TwitterRestStatusTable(None, None, None, None, None, None)
        row = table._row(tweet6)
        self.assertIsInstance(row[0], datetime)
        self.assertEqual("847804888365117440", row[1])
        self.assertEqual("jlittman_dev", row[2])
        self.assertEqual(None, row[3])
        self.assertEqual(0, row[4])
        self.assertEqual(0, row[5])
        self.assertEqual(0, row[6])
        self.assertEqual(0, row[7])
        self.assertEqual("http://twitter.com/jlittman_dev/status/847804888365117440", row[11])
        self.assertEqual("@justin_littman Some of the changes went live. This is going to be an example for a blog "
                         "post I'm writing that will be available at: https://t.co/MfQy5wTWBc",
                         row[12])
        self.assertEqual("No", row[13])
        self.assertEqual("No", row[14])
        self.assertEqual("", row[15])
        self.assertEqual("https://t.co/MfQy5wTWBc", row[16])
        self.assertEqual("https://gwu-libraries.github.io/sfm-ui/posts/2017-03-31-extended-tweets", row[17])
        self.assertEqual("", row[18])
        self.assertEqual("", row[19])
        self.assertEqual("", row[20])

    def test_rest_extended_tweet_row(self):
        table = TwitterRestStatusTable(None, None, None, None, None, None)
        row = table._row(tweet7)
        self.assertIsInstance(row[0], datetime)
        self.assertEqual("847804888365117440", row[1])
        self.assertEqual("jlittman_dev", row[2])
        self.assertEqual('', row[3])
        self.assertEqual(0, row[4])
        self.assertEqual(0, row[5])
        self.assertEqual(0, row[6])
        self.assertEqual(0, row[7])
        self.assertEqual("http://twitter.com/jlittman_dev/status/847804888365117440", row[11])
        self.assertEqual("@justin_littman Some of the changes went live. This is going to be an example for a blog "
                         "post I'm writing that will be available at: https://t.co/MfQy5wTWBc",
                         row[12])
        self.assertEqual("No", row[13])
        self.assertEqual("No", row[14])
        self.assertEqual("", row[15])
        self.assertEqual("https://t.co/MfQy5wTWBc", row[16])
        self.assertEqual("https://gwu-libraries.github.io/sfm-ui/posts/2017-03-31-extended-tweets", row[17])
        self.assertEqual("", row[18])
        self.assertEqual("", row[19])
        self.assertEqual("", row[20])

    def test_quote_nested_in_tweet(self):
        table = TwitterRestStatusTable(None, None, None, None, None, None)
        row = table._row(tweet8)
        self.assertIsInstance(row[0], datetime)
        self.assertEqual("918735887264972800", row[1])
        self.assertEqual("RT @ClimateCentral: Wildfire season in the American West is now two and a half months longer than it was 40 years ago. Our wildfire report…",
                         row[12])
        self.assertEqual("Yes", row[13])
        self.assertEqual("No", row[14])
