from sfmutils.exporter import BaseExporter
from twitter_stream_warc_iter import TwitterStreamWarcIter
from twitter_rest_exporter import BaseTwitterStatusTable

import logging

log = logging.getLogger(__name__)

QUEUE = "twitter_stream_exporter"
FILTER_ROUTING_KEY = "export.start.twitter.twitter_filter"
SAMPLE_ROUTING_KEY = "export.start.twitter.twitter_sample"


class TwitterStreamStatusTable(BaseTwitterStatusTable):
    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids, segment_row_size=None):
        BaseTwitterStatusTable.__init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids,
                                        TwitterStreamWarcIter, segment_row_size)


class TwitterStreamExporter(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None, warc_base_path=None):
        log.info("Initing TwitterStreamExporter")
        BaseExporter.__init__(self, api_base_url, TwitterStreamWarcIter, TwitterStreamStatusTable, working_path,
                              mq_config=mq_config, warc_base_path=warc_base_path)

if __name__ == "__main__":
    TwitterStreamExporter.main(TwitterStreamExporter, QUEUE, [FILTER_ROUTING_KEY, SAMPLE_ROUTING_KEY])
