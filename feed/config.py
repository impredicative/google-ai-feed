import datetime
import logging.config
import os
import re
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


BASE_URL = 'https://research.google'
CACHE_TTL = datetime.timedelta(hours=3).total_seconds()
FEED_DESCRIPTION = 'As a disclaimer, this is an unofficial feed and has no affiliation with Google.'
FEED_TITLE = 'Google AI publications RSS feed (unofficial)'
FILENAME_TO_ID_REGEX = re.compile(r'^pub(?P<id>\d+)\.html')
LOCALE = 'en_US.UTF-8'
MAX_ENTRIES = 100
PUB_URL_FORMAT = f'{BASE_URL}/pubs/pub{{pub_id}}'
REQUEST_HOME_URL = f'{BASE_URL}/pubs/'
REQUEST_HOME_URL_TIMEOUT = 30
REQUEST_DATA_URL_TIMEOUT = 60
REQUEST_DATA_URL_REGEX = re.compile(br"var\ publicationsJsonPath\ =\ '(?P<path>[^\.]+\.json)';")
RESEARCH_AREAS = {
    'Data Mining and Modeling',
    'Machine Intelligence',
    'Machine Perception',
    'Machine Translation',
    'Natural Language Processing',
    'Robotics',
}
ON_SERVERLESS = bool(os.getenv('GCLOUD_PROJECT'))
PACKAGE_NAME = Path(__file__).parent.stem
REPO_URL = 'https://github.com/ml-feeds/google-ai-feed'

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '[%(relativeCreated)i] %(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
        'serverless': {
            'format': '%(thread)x:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'serverless' if ON_SERVERLESS else 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'chardet': {'level': 'WARNING'},
        PACKAGE_NAME: {
            'level': 'INFO' if ON_SERVERLESS else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
         },
    },
}

