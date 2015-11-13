FROM python:2.7
MAINTAINER Justin Littman <justinlittman@gwu.edu>

RUN pip install --upgrade pip
#This pre-fetches the most recent requirements.txt.
#TODO: Temporary approach
ADD https://github.com/gwu-libraries/sfm-utils/raw/sfm_t46-twitter_harvester/requirements.txt /tmp/
RUN pip install --process-dependency-links -r /tmp/requirements.txt
#TODO: Change this to master
ADD https://github.com/gwu-libraries/sfm-twitter-harvester/raw/sfm_t46-twitter_harvester/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt --process-dependency-links --trusted-host github.com --allow-external warcprox-dev
RUN pip install appdeps
WORKDIR /opt/sfm-twitter-harvester
CMD pip install -r requirements.txt --upgrade \
    && appdeps.py --port-wait mq:5672 \
    && python twitter_harvester.py service mq $MQ_ENV_RABBITMQ_DEFAULT_USER $MQ_ENV_RABBITMQ_DEFAULT_PASS