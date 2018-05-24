#!/usr/bin/env bash
set -e

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait mq:5672 --port-wait api:8080 --file-wait /sfm-data/collection_set --file-wait /sfm-data/containers --file-wait /sfm-data/export \

echo "Starting harvester"
exec gosu sfm python twitter_stream_exporter.py --debug=$DEBUG service mq $RABBITMQ_USER $RABBITMQ_PASSWORD http://api:8080 /sfm-data/containers/$HOSTNAME
