# sfm-twitter-harvester (stream) dev docker container

A docker container for running sfm-flickr-harvester (stream) as a service.

In this container, the code is external to the container and shared with 
the container as a volume.

The code must be mounted as `/opt/sfm-twitter-harvester`. For example, 
`-v=~/my_code/sfm-twitter-harvester:/opt/sfm-flickr-harvester`.

This container also requires a link to a container running the queue. This
must be linked with the alias `mq`.  For example, `--link rabbitmq:mq`. 