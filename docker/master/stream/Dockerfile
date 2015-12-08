FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

RUN apt-get update && apt-get install -y \
    wget \
    supervisor \
    zip
#Upgrade pip
RUN pip install --upgrade pip
RUN wget --no-check-certificate https://github.com/gwu-libraries/sfm-twitter-harvester/archive/master.zip
RUN unzip master.zip
RUN mv sfm-twitter-harvester-master /opt/sfm-twitter-harvester
WORKDIR /opt/sfm-twitter-harvester
RUN pip install -r requirements.txt
RUN pip install appdeps
#Configure supervisor
VOLUME /etc/supervisor/conf.d
CMD appdeps.py --port-wait mq:5672 \
    && supervisord -c /etc/supervisor/supervisord.conf \
    && stream_consumer.py mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS twitter_harvester harvest.start.twitter.twitter_filter /opt/sfm-twitter-harvester/twitter_harvester.py
