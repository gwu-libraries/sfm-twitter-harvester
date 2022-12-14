#!/usr/bin/env bash
set -e

# See https://medium.com/@gchudnov/trapping-signals-in-docker-containers-7a57fdda7d86#.q7t4hhjx9

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait ${SFM_RABBITMQ_HOST}:${SFM_RABBITMQ_PORT} --file-wait /sfm-collection-set-data/collection_set --file-wait /sfm-containers-data/containers

# if filter streams were running under supervisor in 2.3 or earlier, replace old sfm-data paths with 2.4+ paths
if  [ "$(ls -A /etc/supervisor/conf.d)" ]
then
  sed -i.bak 's/sfm-data/sfm-containers-data/' /etc/supervisor/conf.d/*.conf
  sed -i.bak 's/sfm-data/sfm-collection-set-data/' /etc/supervisor/conf.d/*.json
fi

echo "Starting supervisor"
supervisord -c /etc/supervisor/supervisord.conf

echo "Starting stream consumer"
# exec makes this take the pid of the script, which should be pid 1.
exec stream_consumer.py $SFM_RABBITMQ_HOST $SFM_RABBITMQ_USER $SFM_RABBITMQ_PASSWORD twitter_harvester harvest.start.twitter.twitter_filter,harvest.start.twitter.twitter_sample,harvest.start.twitter2.twitter_filter_stream /opt/sfm-twitter-harvester/twitter_harvester.py /sfm-containers-data/containers/$HOSTNAME --debug=$DEBUG --debug-warcprox=$DEBUG_WARCPROX --tries=$HARVEST_TRIES
