FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

ADD https://raw.githubusercontent.com/gwu-libraries/sfm-twitter-harvester/master/requirements/requirements.apt /tmp/
RUN apt-get update && apt-get install -y \
    git=1:2.1.4-2.1+deb8u1
RUN cat /tmp/requirements.apt | tr "\n" " " | xargs apt-get install -y
RUN pip install pip==7.1.2
#This pre-fetches the most recent requirements.txt.
ADD https://raw.githubusercontent.com/gwu-libraries/sfm-twitter-harvester/master/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN pip install appdeps
#Configure supervisor
VOLUME /etc/supervisor/conf.d
WORKDIR /opt/sfm-twitter-harvester
CMD cd /opt/sfm-utils \
    && python setup.py develop \
    && cd /opt/sfm-twitter-harvester \
    && pip install -r requirements.txt --upgrade \
    && appdeps.py --port-wait mq:5672 \
    && supervisord -c /etc/supervisor/supervisord.conf \
    && stream_consumer.py mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS twitter_harvester harvest.start.twitter.twitter_filter /opt/sfm-twitter-harvester/twitter_harvester.py --debug=$DEBUG
