from sfmutils.exporter import BaseExporter
from twitter_stream_warc_iter import TwitterStreamWarcIter
from twitter_stream_warc_iter import TwitterStreamWarcIter2
from twitter_rest_exporter import BaseTwitterStatusTable
from twitter_rest_exporter import BaseTwitterTwoStatusTable


import logging

log = logging.getLogger(__name__)

QUEUE = "twitter_stream_exporter"
QUEUE2 = "twitter_stream_exporter2"
FILTER_ROUTING_KEY = "export.start.twitter.twitter_filter"
SAMPLE_ROUTING_KEY = "export.start.twitter.twitter_sample"
FILTER_STREAM_ROUTING_KEY = "harvest.start.twitter2.twitter_filter_stream"


class TwitterStreamStatusTable(BaseTwitterStatusTable):
    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids, segment_row_size=None):
        BaseTwitterStatusTable.__init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids,
                                        TwitterStreamWarcIter, segment_row_size)


class TwitterStreamExporter(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None, warc_base_path=None):
        log.info("Initing TwitterStreamExporter")
        BaseExporter.__init__(self, api_base_url, TwitterStreamWarcIter, TwitterStreamStatusTable, working_path,
                              mq_config=mq_config, warc_base_path=warc_base_path)


#for ver2

class TwitterStreamStatusTable2(BaseTwitterStatusTable):
    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids, segment_row_size=None):
        BaseTwitterTwoStatusTable.__init__(self, warc_paths, dedupe, item_date_start, item_date_end, seed_uids,
                                        TwitterStreamWarcIter2, segment_row_size)


class TwitterStreamExporter2(BaseExporter):
    def __init__(self, api_base_url, working_path, mq_config=None, warc_base_path=None):
        log.info("Initing TwitterStreamExporter2")
        BaseExporter.__init__(self, api_base_url, TwitterStreamWarcIter2, TwitterStreamStatusTable2, working_path,
                              mq_config=mq_config, warc_base_path=warc_base_path)

#for ver2

# if __name__ == "__main__":
#     TwitterStreamExporter.main(TwitterStreamExporter, QUEUE, [FILTER_ROUTING_KEY, SAMPLE_ROUTING_KEY])


#for ver2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--twitter_version", default='2')
    # To remove argument before passing to the wrapped function
    # Following example here: https://stackoverflow.com/questions/35733262/is-there-any-way-to-instruct-argparse-python-2-7-to-remove-found-arguments-fro
    args, extras = parser.parse_known_args()
    sys.argv = sys.argv[:1] + extras
    if args.twitter_version == '2':
        TwitterRestExporter2.main(TwitterRestExporter2, QUEUE2, [FILTER_STREAM_ROUTING_KEY])
    else:
        TwitterRestExporter.main(TwitterRestExporter, QUEUE,
                             [FILTER_ROUTING_KEY, SAMPLE_ROUTING_KEY])


#ver2
