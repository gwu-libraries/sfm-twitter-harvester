from __future__ import absolute_import
import tests
from mock import MagicMock, patch, call
from twitter_rest_harvester import TwitterRestHarvester
from twarc import Twarc
from tests.tweets import tweet1, tweet2
from sfmutils.state_store import DictHarvestStateStore

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


class TestTwitterRestHarvester(tests.TestCase):
    @patch("twitter_rest_harvester.Twarc", autospec=True)
    def test_search(self, mock_twarc_class):

        mock_twarc = MagicMock(spec=Twarc)
        #Expecting 2 searches. First returns 2 tweets. Second returns none.
        mock_twarc.search.side_effect = [(tweet1, tweet2), ()]
        #Return mock_twarc when instantiating a twarc.
        mock_twarc_class.side_effect = [mock_twarc]

        harvester = TwitterRestHarvester(None, None, None, None, None, None, skip_connection=True)
        state_store = DictHarvestStateStore()

        harvest_result = harvester.harvest_seeds(base_message, state_store)

        self.assertDictEqual({"tweet": 2}, harvest_result.summary)
        self.assertSetEqual(set(["http://bit.ly/1ipwd0B"]), harvest_result.urls_as_set())
        mock_twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call("gwu", since_id=None), call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        #Nothing added to state
        self.assertEqual(0, len(state_store._state))

    @patch("twitter_rest_harvester.Twarc", autospec=True)
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

        harvester = TwitterRestHarvester(None, None, None, None, None, None, skip_connection=True)
        state_store = DictHarvestStateStore()
        state_store.set_state("twitter_rest_harvester", "gwu.since_id", 605726286741434400)

        harvest_result = harvester.harvest_seeds(message, state_store)

        self.assertDictEqual({"tweet": 1}, harvest_result.summary)
        self.assertSetEqual(set(["http://bit.ly/1ipwd0B"]), harvest_result.urls_as_set())
        twarc_class.assert_called_once_with(tests.TWITTER_CONSUMER_KEY, tests.TWITTER_CONSUMER_SECRET,
                                            tests.TWITTER_ACCESS_TOKEN, tests.TWITTER_ACCESS_TOKEN_SECRET)
        self.assertEqual([call("gwu", since_id=605726286741434400), call("gelman", since_id=None)], mock_twarc.search.mock_calls)
        #State updated
        self.assertEqual(660065173563158500, state_store.get_state("twitter_rest_harvester", "gwu.since_id"))


