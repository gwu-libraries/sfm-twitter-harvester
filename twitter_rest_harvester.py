from __future__ import absolute_import
import argparse
import logging
import datetime
import pika
import json
import tempfile
import os
import shutil
import re
import hashlib
from twarc import Twarc
from sfmutils.state_store import JsonHarvestStateStore
from sfmutils.harvester import HarvestResult, STATUS_SUCCESS, STATUS_FAILURE, Msg, CODE_UNKNOWN_ERROR
from sfmutils.warcprox import warced
from sfmutils.utils import safe_string

log = logging.getLogger(__name__)


class BaseHarvester():
    #TODO: Move this into sfmutils
    def __init__(self, host, username, password, exchange, queue, routing_key, skip_connection=False):
        self.queue = queue
        self.exchange = exchange

        #Creating a connection can be skipped for testing purposes
        if not skip_connection:
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(host=host, credentials=credentials)
            self._connection = pika.BlockingConnection(parameters)
            channel = self._connection.channel()
            #Declare sfm_exchange
            channel.exchange_declare(exchange=exchange,
                                     type="topic", durable=True)
            #Declare harvester queue
            channel.queue_declare(queue=queue,
                                  durable=True)
            #Bind
            channel.queue_bind(exchange=exchange,
                               queue=queue, routing_key=routing_key)

            channel.close()

    def consume(self):
        channel = self._connection.channel()
        channel.basic_qos(prefetch_count=1)
        log.info("Waiting for messages from %s", self.queue)
        channel.basic_consume(self._callback, queue=self.queue)
        channel.start_consuming()

    def _callback(self, channel, method, _, body):
        """
        Callback for receiving harvest message.
        """
        log.info("Harvesting by message")

        #Acknowledge the message
        log.debug("Acking message")
        channel.basic_ack(delivery_tag=method.delivery_tag)

        start_date = datetime.datetime.now()
        message = json.loads(body)
        log.debug("Message is %s" % json.dumps(message, indent=4))
        harvest_id = message["id"]
        collection_id = message["collection"]["id"]
        collection_path = message["collection"]["path"]

        prefix = safe_string(harvest_id)
        #Create a temp directory for WARCs
        warc_temp_dir = tempfile.mkdtemp(prefix=prefix)
        state_store = self.get_state_store(message)
        try:
            with warced(prefix, warc_temp_dir):
                harvest_result = self.harvest_seeds(message, state_store)
        except Exception as e:
            log.exception(e)
            harvest_result = HarvestResult()
            harvest_result.success = False
            harvest_result.errors.append(Msg(CODE_UNKNOWN_ERROR, str(e)))

        if harvest_result.success:
            #Send web harvest message
            self._send_web_harvest_message(channel, harvest_id, collection_id,
                                           collection_path, harvest_result.urls_as_set())
            #Process warc files
            print warc_temp_dir
            for warc_filename in self._list_warcs(warc_temp_dir):
                #Move the warc
                dest_warc_filepath = self._move_file(warc_filename,
                                                     warc_temp_dir, self._path_for_warc(collection_path, warc_filename))
                #Send warc created message
                self._send_warc_created_message(channel, collection_id, collection_path, self._warc_id(warc_filename),
                                                dest_warc_filepath)

        #Delete temp dir
        if os.path.exists(warc_temp_dir):
            shutil.rmtree(warc_temp_dir)
        #Close state store
        state_store.close()
        self._send_status_message(channel, method.routing_key, harvest_id, harvest_result, start_date)

    def harvest_seeds(self, message, state_store):
        """
        Performs a harvest based on the seeds contained in the message.
        :param message: the message
        :param state_store: a state store
        :return: a HarvestResult
        """
        pass

    def get_state_store(self, message):
        """
        Gets a state store for the harvest.
        """
        return JsonHarvestStateStore(message["collection"]["path"])

    @staticmethod
    def _list_warcs(path):
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and
                (f.endswith(".warc") or f.endswith(".warc.gz"))]

    @staticmethod
    def _path_for_warc(collection_path, filename):
        m = re.search("-(\d{4})(\d{2})(\d{2})(\d{2})\d{7}-", filename)
        assert m
        return "/".join([collection_path, m.group(1), m.group(2), m.group(3), m.group(4)])

    @staticmethod
    def _warc_id(warc_filename):
        return warc_filename.replace(".warc", "").replace(".gz", "")

    @staticmethod
    def _move_file(filename, src_path, dest_path):
        src_filepath = os.path.join(src_path, filename)
        dest_filepath = os.path.join(dest_path, filename)
        log.debug("Moving %s to %s", src_filepath, dest_filepath)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        shutil.move(src_filepath, dest_filepath)
        return dest_filepath

    def _publish_message(self, routing_key, message, channel):
        message_body = json.dumps(message, indent=4)
        log.debug("Sending message to sfm_exchange with routing_key %s. The body is: %s", routing_key, message_body)
        channel.basic_publish(exchange=self.exchange,
                              routing_key=routing_key,
                              properties=pika.spec.BasicProperties(content_type="application/json",
                                                                   delivery_mode=2),
                              body=message_body)

    def _send_web_harvest_message(self, channel, harvest_id, collection_id, collection_path, urls):
        message = {
            #This will be unique
            "id": "{}:{}".format(self.__class__.__name__, harvest_id),
            "parent_id": harvest_id,
            "type": "web",
            "seeds": [],
            "collection": {
                "id": collection_id,
                "path": collection_path
            }
        }
        for url in urls:
            message["seeds"].append({"token": url})

        self._publish_message("harvest.start.web", message, channel)

    def _send_status_message(self, channel, harvest_routing_key, harvest_id, harvest_result, start_date):
        #Just add additional info to job message
        message = {
            "id": harvest_id,
            "status": STATUS_SUCCESS if harvest_result.success else STATUS_FAILURE,
            "infos": [msg.to_map() for msg in harvest_result.infos],
            "warnings": [msg.to_map() for msg in harvest_result.warnings],
            "errors": [msg.to_map() for msg in harvest_result.errors],
            "date_started": start_date.isoformat(),
            "date_ended": datetime.datetime.now().isoformat(),
            "summary": harvest_result.summary,
            "token_updates": harvest_result.token_updates,
            "uids": harvest_result.uids
        }

        #Routing key may be none
        status_routing_key = harvest_routing_key.replace("start", "status")
        self._publish_message(status_routing_key, message, channel)

    def _send_warc_created_message(self, channel, collection_id, collection_path, warc_id, warc_path):
        message = {
            "collection": {
                "id": collection_id,
                "path": collection_path

            },
            "warc": {
                "id": warc_id,
                "path": warc_path,
                "date_created": datetime.datetime.fromtimestamp(os.path.getctime(warc_path)).isoformat(),
                "bytes": os.path.getsize(warc_path),
                "sha1": hashlib.sha1(open(warc_path).read()).hexdigest()
            }
        }
        self._publish_message("warc_created", message, channel)


class TwitterRestHarvester(BaseHarvester):
    def harvest_seeds(self, message, state_store):
        harvest_result = HarvestResult()
        #Create a twarc
        twarc = self._create_twarc(message)
        #Dispatch message based on type.
        harvest_type = message.get("type")
        log.debug("Harvest type is %s", harvest_type)
        if harvest_type == "twitter_search":
            harvest_result = self.search(message, twarc, state_store)
        else:
            raise KeyError
        return harvest_result


    @staticmethod
    def _create_twarc(message):
        return Twarc(message["credentials"]["consumer_key"],
                     message["credentials"]["consumer_secret"],
                     message["credentials"]["access_token"],
                     message["credentials"]["access_token_secret"])

    def search(self, message, twarc, state_store):
        harvest_result = HarvestResult()
        incremental = message.get("options", {}).get("incremental", False)

        for seed in message.get("seeds", []):
            query = seed.get("token")
            #Get since_id from state_store
            since_id = state_store.get_state(__name__, "{}.since_id".format(query)) if incremental else None

            tweet_count, urls, max_tweet_id = self._process_tweets(twarc.search(query, since_id=since_id))
            log.debug("Searching on %s since %s returned %s tweets.", query, since_id, tweet_count)

            #Update state store
            if incremental and max_tweet_id:
                state_store.set_state(__name__, "{}.since_id".format(query), max_tweet_id)
            #Update total count
            harvest_result.increment_summary("tweet", tweet_count)
            #Add urls to merged_urls
            harvest_result.urls.extend(urls)

        return harvest_result

    @staticmethod
    def _process_tweets(tweets):
        urls = set()
        tweet_count = 0
        max_tweet_id = None
        for tweet in tweets:
            if "text" in tweet:
                max_tweet_id = max(max_tweet_id, tweet.get("id"))
                tweet_count += 1
                if "urls" in tweet["entities"]:
                    for url in tweet["entities"]["urls"]:
                        urls.add(url["expanded_url"])
                if "media" in tweet["entities"]:
                    for media in tweet["entities"]["media"]:
                        urls.add(media["media_url"])
        return tweet_count, urls, max_tweet_id

if __name__ == "__main__":
    #TODO: Make this re-usable.

    #Logging
    logging.basicConfig(format='%(asctime)s: %(name)s --> %(message)s', level=logging.DEBUG)

    #Arguments
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    service_parser = subparsers.add_parser("service", help="Run harvesting service that consumes messages from "
                                                           "messaging queue.")
    service_parser.add_argument("host")
    service_parser.add_argument("username")
    service_parser.add_argument("password")

    seed_parser = subparsers.add_parser("seed", help="Harvest based on a seed file.")
    seed_parser.add_argument("filepath", help="Filepath of the seed file.")

    args = parser.parse_args()

    # if args.command == "service":
    #     consumer = FlickrConsumer(host=args.host, username=args.username, password=args.password)
    #     consumer.consume()
    # elif args.command == "seed":
    #     consumer = FlickrConsumer()
    #     with open(args.filepath) as seeds_file:
    #         seeds = seeds_file.read()
    #     resp = consumer.harvest_seeds(seeds)
    #     if resp:
    #         log.info("Result is: %s", resp)
    #         sys.exit(0)
    #     else:
    #         log.warning("Result is: %s", resp)
    #         sys.exit(1)
