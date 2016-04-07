FROM python@sha256:ad39551743b356efda7c61f46019b97d49d1aab01b97f0e6d87c9b34326f3bfe
#Python 2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

ADD https://raw.githubusercontent.com/gwu-libraries/sfm-twitter-harvester/master/requirements/requirements.apt /tmp/
RUN apt-get update && apt-get install -y \
    git=1:2.1.4-2.1+deb8u1 \
    zip=3.0-8
RUN cat /tmp/requirements.apt | tr "\n" " " | xargs apt-get install -y
#Upgrade pip
RUN pip install pip==7.1.2
WORKDIR /tmp
ADD https://github.com/gwu-libraries/sfm-twitter-harvester/archive/master.zip /tmp/
RUN unzip master.zip
RUN mv sfm-twitter-harvester-master /opt/sfm-twitter-harvester
WORKDIR /opt/sfm-twitter-harvester
RUN pip install -r requirements/master.txt
RUN pip install appdeps
#Configure supervisor
VOLUME /etc/supervisor/conf.d
CMD appdeps.py --port-wait mq:5672 \
    && supervisord -c /etc/supervisor/supervisord.conf \
    && stream_consumer.py mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS twitter_harvester harvest.start.twitter.twitter_filter,harvest.start.twitter.twitter_sample /opt/sfm-twitter-harvester/twitter_harvester.py --debug=$DEBUG
