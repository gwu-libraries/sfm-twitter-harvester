#!/usr/bin/env bash
set -e

# See https://medium.com/@gchudnov/trapping-signals-in-docker-containers-7a57fdda7d86#.q7t4hhjx9

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait ${SFM_RABBITMQ_HOST}:${SFM_RABBITMQ_PORT}  --file-wait /sfm-collection-set-data/collection_set --file-wait /sfm-collection-set-data/containers

echo "Starting supervisor"
supervisord -c /etc/supervisor/supervisord.conf

echo "Starting stream consumer"
# exec makes this take the pid of the script, which should be pid 1.
exec stream_consumer.py $SFM_RABBITMQ_HOST $SFM_RABBITMQ_USER $SFM_RABBITMQ_PASSWORD twitter_harvester harvest.start.twitter.twitter_filter,harvest.start.twitter.twitter_sample /opt/sfm-twitter-harvester/twitter_harvester.py /sfm-containers-data/containers/$HOSTNAME --debug=$DEBUG --debug-warcprox=$DEBUG_WARCPROX --tries=$HARVEST_TRIES
