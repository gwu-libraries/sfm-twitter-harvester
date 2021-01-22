#!/usr/bin/env bash
set -e

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait mq:5672 --file-wait /sfm-collection-set-data/collection_set --file-wait /sfm-collection-set-data/containers

echo "Starting harvester"
exec gosu sfm python twitter_harvester.py --debug=$DEBUG --debug-warcprox=$DEBUG_WARCPROX service mq $RABBITMQ_USER $RABBITMQ_PASSWORD /sfm-containers-data/containers/$HOSTNAME --tries=$HARVEST_TRIES --priority-queues=$PRIORITY_QUEUES
