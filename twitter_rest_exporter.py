from sfmutils.exporter import BaseExporter, BaseTable
from twitter_rest_warc_iter import TwitterRestWarcIter
import logging
import twarc.json2csv

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_exporter"
SEARCH_ROUTING_KEY = "export.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "export.start.twitter.twitter_user_timeline"


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


class TwitterRestStatusTable(BaseTwitterStatusTable):
    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, segment_row_size=None):
        BaseTwitterStatusTable.__init__(self, warc_paths, dedupe,
                                        item_date_start, item_date_end,
                                        seed_uids, TwitterRestWarcIter,
                                        segment_row_size)


class TwitterRestExporter(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None,
                 warc_base_path=None):
        BaseExporter.__init__(self, api_base_url, TwitterRestWarcIter,
                              TwitterRestStatusTable, working_path,
                              mq_config=mq_config,
                              warc_base_path=warc_base_path)


if __name__ == "__main__":
    TwitterRestExporter.main(TwitterRestExporter, QUEUE,
                             [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
