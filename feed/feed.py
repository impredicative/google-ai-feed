import locale
import logging
import textwrap

import cachetools.func
import feedgen.feed
import requests

from feed import config
from feed.util.humanize import humanize_len

locale.setlocale(locale.LC_ALL, config.LOCALE)
config.configure_logging()

log = logging.getLogger(__name__)


def filename_to_id(filename: str) -> int:
    return int(config.FILENAME_TO_ID_REGEX.fullmatch(filename).groupdict()['id'])


class Feed:
    def __init__(self):
        self._areas = {f'research-area-{a.lower().replace(" ", "-")}' for a in config.RESEARCH_AREAS}

    @staticmethod
    def _init_feed() -> feedgen.feed.FeedGenerator:
        feed = feedgen.feed.FeedGenerator()
        feed.title(config.FEED_TITLE)
        feed.link(href=config.REPO_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)
        return feed

    @cachetools.func.ttl_cache(maxsize=1, ttl=config.CACHE_TTL)
    def feed(self) -> bytes:
        log.debug('Reading %s', config.REQUEST_URL)
        pubs = requests.get(config.REQUEST_URL, timeout=config.REQUEST_TIMEOUT).json()['publications']
        log.info('Response for request URL has %s entries.', f'{len(pubs):n}')
        log.info('The %s whitelisted research areas are: %s',
                 len(config.RESEARCH_AREAS), ', '.join(config.RESEARCH_AREAS))
        pubs = [pub for pub in pubs if not set(pub['tag_pks']).isdisjoint(self._areas)]  # Remove null intersections.
        log.info('%s of these entries exist for the whitelisted research areas.', len(pubs))
        pubs = [p for p in pubs if ('URL\t' in p['bibtex'])]  # Remove entries without a download link.
        log.info('%s of these entries have a download link.', len(pubs))
        for pub in pubs:
            pub[':id'] = filename_to_id(pub['filename_html'])
        pubs.sort(key=lambda pub: pub[':id'], reverse=True)
        pubs = pubs[:config.MAX_ENTRIES]

        feed = self._init_feed()
        for idx, pub in enumerate(pubs):
            title = pub['title']
            desc = textwrap.shorten(pub['description_html'], float('inf'))  # type: ignore
            desc = ''.join(c for c in desc if c.isprintable())
            url = config.PUB_URL_FORMAT.format(pub_id=pub[':id'])
            guid = str(pub[':id'])
            categories = pub['tag_pks']  # Often starts with "research-area-" or "team-".

            entry = feed.add_entry(order='append')
            entry.title(title)
            entry.link(href=url)
            entry.guid(guid, permalink=False)
            entry.description(desc)
            for category in categories:
                entry.category(term=category)

            log.debug('Added pub #%s having ID %s, title %s (%s), and categories: %s',
                      idx + 1, pub[':id'], repr(title), pub['year'], ', '.join(c for c in categories))

        text: bytes = feed.rss_str(pretty=True)
        log.info('Output feed has %s items and size %s.', len(pubs), humanize_len(text))
        return text
