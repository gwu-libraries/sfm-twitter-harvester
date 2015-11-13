FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

RUN apt-get update && apt-get install -y \
    supervisor \
    git
RUN pip install --upgrade pip
#This pre-fetches the most recent requirements.txt.
#TODO: Temporary approach
ADD https://github.com/gwu-libraries/sfm-utils/raw/sfm_t46-twitter_harvester/requirements.txt /tmp/
RUN pip install --process-dependency-links -r /tmp/requirements.txt
#TODO: Change this to master
ADD https://github.com/gwu-libraries/sfm-twitter-harvester/raw/sfm_t46-twitter_harvester/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN pip install appdeps
#Configure supervisor
VOLUME /etc/supervisor/conf.d
WORKDIR /opt/sfm-twitter-harvester
CMD pip install --upgrade -r requirements.txt \
    && appdeps.py --port-wait mq:5672 \
    && supervisord -c /etc/supervisor/supervisord.conf \
    && stream_consumer.py mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS twitter_harvester harvest.start.twitter.twitter_filter /opt/sfm-twitter-harvester/twitter_harvester.py