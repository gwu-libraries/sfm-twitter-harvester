from sfmutils.exporter import BaseExporter, BaseTable
from twitter_rest_warc_iter import TwitterRestWarcIter, TwitterRestWarcIter2
import logging
import twarc.json2csv
import argparse
from twarc_csv import dataframe_converter

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_exporter"
SEARCH_ROUTING_KEY = "export.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "export.start.twitter.twitter_user_timeline"
SEARCH2_ROUTING_KEY = "harvest.start.twitter2.twitter_search_2"
TIMELINE2_ROUTING_KEY = "harvest.start.twitter2.twitter_user_timeline_2"
ACADEMIC_SEARCH_ROUTING_KEY = "harvest.start.twitter2.twitter_academic_search"

class BaseTwitterTwoStatusTable(BaseTable):
    """
    PETL Table for Twitter statuses for v. 2 API.
    """

    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, warc_iter_cls, segment_row_size):
        self.DataFrameConverter = dataframe_converter.DataFrameConverter
        BaseTable.__init__(self, warc_paths, dedupe, item_date_start,
                           item_date_end, seed_uids, warc_iter_cls,
                           segment_row_size)

    def _header_row(self):
        '''
        Returns CSV columns from DataFrameConverter
        '''
        return self.DataFrameConverter().columns

    def _row(self, item):
        '''
        Returns a single row for the CSV, using the twarc_csv DataFrameConverter class.
        (Probably need to refactor for the sake of greater efficiency, since this creates a new DataFrame for every single Tweet.)
        '''
        dfc = self.DataFrameConverter()
        df = dfc.process(item)
        # DataFrame.values returns an array of rows -- we want only a single row
        return df.values[0]

    def id_field(self):
        return "id"


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
        return twarc.json2csv.get_headings()

    def _row(self, item):
        return twarc.json2csv.get_row(item, excel=True)

    def id_field(self):
        return "id"


def create_twitter_status_table_class(twitter_table_cls, twitter_warc_iter_cls=TwitterRestWarcIter):
    '''
    Helper function to create a class dynamically based on the provided arguments.
    :param twitter_table_cls: should be either BaseTwitterStatusTable or BaseTwitterTwoStatusTable
    :param twitter_warc_iter_cls: should be either TwitterRestWarcIter or TwitterRestWarcIter2
    '''
    class TwitterRestStatusTable(twitter_table_cls):
        def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, segment_row_size=None):
            twitter_table_cls.__init__(self, warc_paths, dedupe,
                                        item_date_start, item_date_end,
                                        seed_uids, twitter_warc_iter_cls,
                                        segment_row_size)
    
    return TwitterRestStatusTable


class TwitterRestExporter(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None,
                 warc_base_path=None):
        TwitterRestStatusTable = create_twitter_status_table_class(BaseTwitterStatusTable, TwitterRestWarcIter)
        BaseExporter.__init__(self, api_base_url, TwitterRestWarcIter,
                              TwitterRestStatusTable, working_path,
                              mq_config=mq_config,
                              warc_base_path=warc_base_path)

class TwitterRestExporter2(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None,
                 warc_base_path=None):
        TwitterRestStatusTable = create_twitter_status_table_class(BaseTwitterTwoStatusTable, TwitterRestWarcIter2)
        BaseExporter.__init__(self, api_base_url, TwitterRestWarcIter2,
                              TwitterRestStatusTable, working_path,
                              mq_config=mq_config,
                              warc_base_path=warc_base_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--twitter_version", default='2')
    # To remove argument before passing to the wrapped function
    # Following example here: https://stackoverflow.com/questions/35733262/is-there-any-way-to-instruct-argparse-python-2-7-to-remove-found-arguments-fro
    args, extras = parser.parse_known_args()
    sys.argv = sys.argv[:1] + extras
    if args.twitter_version == '2':
        TwitterRestExporter2.main(TwitterRestExporter2, QUEUE, [SEARCH2_ROUTING_KEY, TIMELINE2_ROUTING_KEY, ACADEMIC_SEARCH_ROUTING_KEY])
    else:
        TwitterRestExporter.main(TwitterRestExporter, QUEUE,
                             [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
