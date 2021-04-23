#!/usr/bin/env bash
set -e

sh /opt/sfm-setup/setup_reqs.sh

echo "Waiting for dependencies"
appdeps.py --wait-secs 60 --port-wait ${SFM_RABBITMQ_HOST}:${SFM_RABBITMQ_PORT} --port-wait api:8080 --file-wait /sfm-collection-set-data/collection_set --file-wait /sfm-containers-data/containers --file-wait /sfm-export-data/export \

echo "Starting harvester"
exec gosu sfm python twitter_rest_exporter.py --debug=$DEBUG service $SFM_RABBITMQ_HOST $SFM_RABBITMQ_USER $SFM_RABBITMQ_PASSWORD http://api:8080 /sfm-containers-data/containers/$HOSTNAME
