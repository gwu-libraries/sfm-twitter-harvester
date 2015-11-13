# sfm-flickr-harvester (rest) master docker container

A docker container for running sfm-twitter-harvester (rest) as a service.

This container requires a link to a container running the queue. This
must be linked with the alias `mq`.  For example, `--link rabbitmq:mq`. 