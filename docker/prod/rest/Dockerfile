FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

ENV sfm_harvester_version 0.1.0
RUN apt-get update && apt-get install -y \
    wget \
    zip
#Upgrade pip
RUN pip install --upgrade pip
RUN wget --no-check-certificate https://github.com/gwu-libraries/sfm-twitter-harvester/archive/${sfm_harvester_version}.zip
RUN unzip ${sfm_harvester_version}.zip
RUN mv sfm-twitter-harvester-${sfm_harvester_version} /opt/sfm-twitter-harvester
WORKDIR /opt/sfm-twitter-harvester
RUN pip install -r requirements.txt
RUN pip install appdeps
CMD appdeps.py --port-wait mq:5672 \
    && python twitter_harvester.py --debug service mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS
