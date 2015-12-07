FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

RUN pip install --upgrade pip
#This pre-fetches the most recent requirements.txt.
ADD https://raw.githubusercontent.com/gwu-libraries/sfm-twitter-harvester/master/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN pip install appdeps
WORKDIR /opt/sfm-twitter-harvester
#This links in sfm-utils as develop.
CMD cd /opt/sfm-utils \
    && python setup.py develop \
    && cd /opt/sfm-twitter-harvester \
    && pip install -r requirements.txt --upgrade \
    && appdeps.py --port-wait mq:5672 \
    && python twitter_harvester.py --debug service mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS
