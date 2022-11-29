import logging
import unittest
import os
import socket

try:
    from .test_config import *
except ImportError:
    TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY", "fake")
    TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET", "fake")
    TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "fake")
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "fake")
    TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "fake")

test_config_available = (TWITTER_CONSUMER_KEY != "fake" and TWITTER_CONSUMER_SECRET != "fake"
                         and TWITTER_ACCESS_TOKEN != "fake" and TWITTER_ACCESS_TOKEN_SECRET != "fake") \
                         or TWITTER_BEARER_TOKEN != "fake"

mq_port_available = True
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect(("mq", 5672))
    except socket.error:
        mq_port_available = False

mq_username = os.environ.get("RABBITMQ_USER")
mq_password = os.environ.get("RABBITMQ_PASSWORD")
integration_env_available = mq_port_available and mq_username and mq_password


class TestCase(unittest.TestCase):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("twitter_rest_harvester").setLevel(logging.DEBUG)
