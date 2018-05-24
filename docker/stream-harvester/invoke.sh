#!/usr/bin/env bash
set -e

# See https://medium.com/@gchudnov/trapping-signals-in-docker-containers-7a57fdda7d86#.q7t4hhjx9

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait mq:5672 --file-wait /sfm-data/collection_set --file-wait /sfm-data/containers

echo "Starting supervisor"
supervisord -c /etc/supervisor/supervisord.conf

echo "Starting stream consumer"
# exec makes this take the pid of the script, which should be pid 1.
exec stream_consumer.py mq $RABBITMQ_USER $RABBITMQ_PASSWORD twitter_harvester harvest.start.twitter.twitter_filter,harvest.start.twitter.twitter_sample /opt/sfm-twitter-harvester/twitter_harvester.py /sfm-data/containers/$HOSTNAME --debug=$DEBUG --debug-warcprox=$DEBUG_WARCPROX --tries=$HARVEST_TRIES
