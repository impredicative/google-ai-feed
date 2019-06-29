import locale
import logging

import cachetools.func
import feedgen.feed
import requests

from feed import config
from feed.util.humanize import humanize_len

locale.setlocale(locale.LC_ALL, config.LOCALE)
config.configure_logging()

log = logging.getLogger(__name__)


def filename_to_id(filename: str) -> int:
    return int(''.join(c for c in filename if c.isdigit()))


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
        log.debug('Reading request URL.')
        pubs = requests.get(config.REQUEST_URL, timeout=config.REQUEST_TIMEOUT).json()['publications']
        log.info('Response for request URL has %s entries.', f'{len(pubs):n}')

        pubs = [pub for pub in pubs if not set(pub['tag_pks']).isdisjoint(self._areas)]  # Remove null intersections
        # pubs = [p for p in pubs if ('(to appear)' not in p['venue_html'])]  # Bad approximation of download avail.
        for pub in pubs:
            pub[':id'] = filename_to_id(pub['filename_html'])
        pubs.sort(key=lambda pub: pub[':id'], reverse=True)
        pubs = pubs[:config.MAX_ENTRIES]

        feed = self._init_feed()
        for idx, pub in enumerate(pubs):
            title = pub['title']
            url = config.PUB_URL_FORMAT.format(pub_id=pub[':id'])
            guid = str(pub[':id'])
            categories = pub['tag_pks']  # Often starts with "research-area-" or "team-".

            entry = feed.add_entry(order='append')
            entry.title(title)
            entry.link(href=url)
            entry.guid(guid, permalink=False)
            entry.description(pub['description_html'])
            for category in categories:
                entry.category(term=category)

            log.debug('Added pub #%s having ID %s, title %s (%s), and categories: %s',
                      idx + 1, pub[':id'], repr(title), pub['year'], ', '.join(c for c in categories))

        text: bytes = feed.rss_str(pretty=True)
        log.info('Output feed has %s items and size %s.', len(pubs), humanize_len(text))
        return text
