from sfmutils.exporter import BaseExporter, BaseTable
from twitter_rest_warc_iter import TwitterRestWarcIter, TwitterRestWarcIter2
import logging
import twarc.json2csv
import argparse
from twarc_csv import dataframe_converter as dc
import sys
from sfmutils.exporter import ExportResult, to_xlsx, to_lineoriented_json, CODE_WARC_MISSING, CODE_NO_WARCS, CODE_BAD_REQUEST
from sfmutils.utils import datetime_now
import iso8601
import os
import shutil
from petl.util.base import dicts as _dicts
import petl
from petl.io.sources import write_source_from_arg
from sfmutils.result import BaseResult, Msg, STATUS_SUCCESS, STATUS_FAILURE, STATUS_RUNNING
import pandas as pd
from itertools import islice, chain

log = logging.getLogger(__name__)

QUEUE = "twitter_rest_exporter"
SEARCH_ROUTING_KEY = "export.start.twitter.twitter_search"
TIMELINE_ROUTING_KEY = "export.start.twitter.twitter_user_timeline"
QUEUE2 = "twitter_rest_exporter2"
SEARCH2_ROUTING_KEY = "export.start.twitter2.twitter_search_2"
TIMELINE2_ROUTING_KEY = "export.start.twitter2.twitter_user_timeline_2"
ACADEMIC_SEARCH_ROUTING_KEY = "export.start.twitter2.twitter_academic_search"

# Maximum size of DataFrame -- may need to adjust experimentally
# Consider making an ENV variable
MAX_DATAFRAME_ROWS = 25000

class BaseTwitterTwoStatusTable(BaseTable):
    """
    PETL Table for Twitter statuses for v. 2 API.
    """

    def __init__(self, warc_paths, dedupe, item_date_start, item_date_end,
                 seed_uids, warc_iter_cls, segment_row_size):
        #self.DataFrameConverter = dataframe_converter.DataFrameConverter
        BaseTable.__init__(self, warc_paths, dedupe, item_date_start,
                           item_date_end, seed_uids, warc_iter_cls,
                           segment_row_size)

    def _header_row(self):
        '''
        Returns CSV columns from DataFrameConverter
        '''
        #return self.DataFrameConverter().columns
        return None

    def _row(self, item):
        '''
        Returns a single row for the CSV, using the twarc_csv DataFrameConverter class.
        (Probably need to refactor for the sake of greater efficiency, since this creates a new DataFrame for every single Tweet.)
        '''
        #dfc = self.DataFrameConverter()
        #df = dfc.process([item])
        # DataFrame.values returns an array of rows -- we want only a single row
        #return df.fillna('').values[0]
        return item

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


def grouper(iterable, n):
    '''Helper class, modified from https://docs.python.org/3/library/itertools.html#itertools-recipes, per the suggestions at https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python. Used to subdivide the export segments into smaller chunks for processing.
    :param iterable: a Python iterable
    :param n: size of groups
    '''
    # TESTING NEEDED to confirm that this is memory efficient
    it = iter(iterable)
    while True:
        chunk_it = islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield chain((first_el,), chunk_it)


def to_twarc2_table(table, filepath, converter, format='csv'):
    '''Uses the twarc-csv module's DataFrameConverter to produce the desired output from a batch of Tweets (JSON).
    :param table: an iterable from the BaseStatusTable's __iter__method (already chunked for size)
    :param filepath: a destination filepath for this output
    :param converter: instance of twarc_csv.dataframe_converter.DataFrameConverter (we accept as param to avoid recreating it on each batch
    :param mode: one of (csv, tsv, xlsx)'''
    # Skip null placeholder for header row -- header will be provided by the DataFrameConverter methods
    table = islice(table, 1, None)
    # Iterate over smaller chunks of the given export segment size, to keep DataFrame memory usage within manageable limits
    # Note that if the segment size is not evenly subdividable by the MAX_DATAFRAME_ROWS, some chunks will be suboptimally small
    try:
        max_rows = int(os.environ['MAX_DATAFRAME_ROWS'])
    except:
        max_rows = MAX_DATAFRAME_ROWS
    for i, rows in enumerate(grouper(table, max_rows)):
        df = converter.process(rows)
        log.debug(f'DataFrame contains {len(df)} rows.')
        # On the first pass, create the file
        if i == 0:
            mode = 'w'
        # On subsequent passes, append
        else:
            mode = 'a'
        if format == 'csv':
            # Only write the header if the file is being created
            df.to_csv(filepath, index=False, mode=mode, header=not os.path.exists(filepath))
        elif format == 'tsv':
            df.to_csv(filepath, index=False, mode=mode, header=not os.path.exists(filepath), sep='\t')
        elif format == 'xlsx':
            # Turn off URL encoding for Excel, otherwise we get warnings 
            with pd.ExcelWriter(filepath, engine='xlsxwriter', mode='w', engine_kwargs={'options': {'strings_to_urls': False}}) as writer:
                df.to_excel(writer, index=False, header=True)
        elif format == 'json':
            # Write to JSON-L format
            # May need to incorporate custom handler from exporter.py
            with open(filepath, mode=mode) as f:
                df.to_json(f, orient='records', lines=True, date_format='iso')


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--twitter_version", default='2')
    # To remove argument before passing to the wrapped function
    # Following example here: https://stackoverflow.com/questions/35733262/is-there-any-way-to-instruct-argparse-python-2-7-to-remove-found-arguments-fro
    args, extras = parser.parse_known_args()
    sys.argv = sys.argv[:1] + extras
    if args.twitter_version == '2':
        TwitterRestExporter2.main(TwitterRestExporter2, QUEUE2, [SEARCH2_ROUTING_KEY, TIMELINE2_ROUTING_KEY, ACADEMIC_SEARCH_ROUTING_KEY])
    else:
        TwitterRestExporter.main(TwitterRestExporter, QUEUE,
                             [SEARCH_ROUTING_KEY, TIMELINE_ROUTING_KEY])
