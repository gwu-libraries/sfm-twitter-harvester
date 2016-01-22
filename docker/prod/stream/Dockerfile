FROM python@sha256:ad39551743b356efda7c61f46019b97d49d1aab01b97f0e6d87c9b34326f3bfe
#Python 2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

ENV sfm_harvester_version 0.1.1
ADD https://raw.githubusercontent.com/gwu-libraries/sfm-twitter-harvester/${sfm_harvester_version}/requirements/requirements.apt /tmp/
RUN apt-get update && apt-get install -y \
    zip=3.0-8
RUN cat /tmp/requirements.apt | tr "\n" " " | xargs apt-get install -y
#Upgrade pip
RUN pip install pip==7.1.2
WORKDIR /tmp
ADD https://github.com/gwu-libraries/sfm-twitter-harvester/archive/${sfm_harvester_version}.zip /tmp/
RUN unzip ${sfm_harvester_version}.zip
RUN mv sfm-twitter-harvester-${sfm_harvester_version} /opt/sfm-twitter-harvester
WORKDIR /opt/sfm-twitter-harvester
RUN pip install -r requirements.txt
RUN pip install appdeps
#Configure supervisor
VOLUME /etc/supervisor/conf.d
CMD appdeps.py --port-wait mq:5672 \
    && supervisord -c /etc/supervisor/supervisord.conf \
    && stream_consumer.py mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS twitter_harvester harvest.start.twitter.twitter_filter /opt/sfm-twitter-harvester/twitter_harvester.py --debug=$DEBUG
