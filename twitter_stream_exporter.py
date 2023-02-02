from sfmutils.exporter import BaseExporter
from twitter_stream_warc_iter import TwitterStreamWarcIter
from twitter_stream_warc_iter import TwitterStreamWarcIter2
from twitter_rest_exporter import BaseTwitterStatusTable
from twitter_rest_exporter import BaseTwitterTwoStatusTable
import argparse
import sys

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

    def on_message(self):
        assert self.message
        export_id = self.message["id"]
        log.info("Performing export %s", export_id)
        log.debug(self.message)
        self.result = ExportResult()
        self.result.started = datetime_now()

        # Send status indicating that it is running
        self._send_response_message(STATUS_RUNNING, self.routing_key, export_id, self.result)

        # Get the WARCs from the API
        collection_id = self.message.get("collection", {}).get("id")
        seed_ids = []
        seed_uids = []
        for seed in self.message.get("seeds", []):
            seed_ids.append(seed["id"])
            seed_uids.append(seed["uid"])

        if (collection_id or seed_ids) and not (collection_id and seed_ids):
            harvest_date_start = self.message.get("harvest_date_start")
            harvest_date_end = self.message.get("harvest_date_end")
            # Only request seed ids if < 20. If use too many, will cause problems calling API.
            # 20 is an arbitrary number
            warc_paths = self._get_warc_paths(collection_id, seed_ids if len(seed_ids) <= 20 else None,
                                              harvest_date_start, harvest_date_end)
            export_format = self.message["format"]
            export_segment_size = self.message["segment_size"]
            export_path = self.message["path"]
            dedupe = self.message.get("dedupe", False)
            item_date_start = iso8601.parse_date(
                self.message["item_date_start"]) if "item_date_start" in self.message else None
            item_date_end = iso8601.parse_date(
                self.message["item_date_end"]) if "item_date_end" in self.message else None
            temp_path = os.path.join(self.working_path, "tmp")
            base_filepath = os.path.join(temp_path, export_id)

            if warc_paths:

                # Clean the temp directory
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                os.makedirs(temp_path)

                # Using pandas/twarc_csv instead of PETL
                twarc_export_formats = ("csv", "tsv", "xlsx", "json")

                # Other possibilities: XML, databases, HDFS
                if export_format == "json_full":
                    self._full_json_export(warc_paths, base_filepath, dedupe, item_date_start, item_date_end, seed_uids,
                                           export_segment_size)
                elif export_format == "dehydrate":
                    tables = self.table_cls(warc_paths, dedupe, item_date_start, item_date_end, seed_uids,
                                            export_segment_size)
                    for idx, table in enumerate(tables):
                        filepath = "{}_{}.txt".format(base_filepath, str(idx + 1).zfill(3))
                        log.info("Exporting to %s", filepath)
                        # Convert Tweet dicts to lists of ID's for petl
                        id_tbl = [[row['id']] for row in table if row]
                        id_tbl = [['id']] + id_tbl
                        petl.totext(id_tbl, filepath, template="{{{}}}\n".format(tables.id_field()))
                elif export_format in twarc_export_formats:
                    # Disable deduplication, because the BaseWARCIter class already handles that (based on user input)
                    converter = dc.DataFrameConverter(allow_duplicates=True)
                    # Can't append to xlsx files from DataFrames using the xlsxwriter engine, so we need to limit the file sizes to the largest size of DataFrame we are willing to accommodate
                    if export_format == 'xlsx':
                        try:
                            export_segment_size = int(os.environ['MAX_DATAFRAME_ROWS'])
                        except:
                            export_segment_size = MAX_DATAFRAME_ROWS
                    tables = self.table_cls(warc_paths, dedupe, item_date_start, item_date_end, seed_uids,
                                            export_segment_size)
                    for idx, table in enumerate(tables):
                        filepath = "{}_{}.{}".format(base_filepath, str(idx + 1).zfill(3),
                                                     export_format)
                        log.debug("Exporting to %s", filepath)
                        to_twarc2_table(table, filepath, converter, format=export_format)
                else:
                    self.result.errors.append(
                        Msg(CODE_UNSUPPORTED_EXPORT_FORMAT, "{} is not supported".format(export_format)))
                    self.result.success = False

                # Move files from temp path to export path
                if os.path.exists(export_path):
                    shutil.rmtree(export_path)
                shutil.move(temp_path, export_path)

            else:
                self.result.errors.append(Msg(CODE_NO_WARCS, "No WARC files from which to export"))
                self.result.success = False

        else:
            self.result.errors.append(Msg(CODE_BAD_REQUEST, "Request export of a seed or collection."))
            self.result.success = False

        self.result.ended = datetime_now()
        self._send_response_message(STATUS_SUCCESS if self.result.success else STATUS_FAILURE, self.routing_key,
                                    export_id, self.result)

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
        TwitterStreamExporter2.main(TwitterStreamExporter2, QUEUE2, [FILTER_STREAM_ROUTING_KEY])
    else:
        TwitterStreamExporter.main(TwitterStreamExporter, QUEUE,
                             [FILTER_ROUTING_KEY, SAMPLE_ROUTING_KEY])


#ver2
