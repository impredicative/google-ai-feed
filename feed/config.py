import datetime
import logging.config
import os
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


CACHE_TTL = datetime.timedelta(hours=3).total_seconds()
FEED_DESCRIPTION_SUFFIX = 'As a disclaimer, this is an unofficial feed and has no affiliation with Google.'
FEED_TITLE_SUFFIX = 'Google AI publications RSS feed (unofficial)'
INPUT_URL = 'https://ai.google/research/pubs/?area=DataMiningandModeling&area=MachineIntelligence&area=MachinePerception&area=MachineTranslation&area=NaturalLanguageProcessing&area=Robotics'
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

