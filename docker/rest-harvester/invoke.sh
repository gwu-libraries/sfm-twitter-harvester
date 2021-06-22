#!/usr/bin/env bash
set -e

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait ${SFM_RABBITMQ_HOST}:${SFM_RABBITMQ_PORT} --file-wait /sfm-collection-set-data/collection_set --file-wait /sfm-containers-data/containers

echo "Starting harvester"
exec gosu sfm python twitter_harvester.py --debug=$DEBUG --debug-warcprox=$DEBUG_WARCPROX service $SFM_RABBITMQ_HOST $SFM_RABBITMQ_USER $SFM_RABBITMQ_PASSWORD /sfm-containers-data/containers/$HOSTNAME --tries=$HARVEST_TRIES --priority-queues=$PRIORITY_QUEUES
