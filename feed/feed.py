import locale
import logging
import re
import textwrap
from typing import cast

import cachetools.func
import feedgen.feed
import requests

from feed import config
from feed.util.humanize import humanize_len

locale.setlocale(locale.LC_ALL, config.LOCALE)
config.configure_logging()

log = logging.getLogger(__name__)


def filename_to_id(filename: str) -> int:
    return int(cast(re.Match, config.FILENAME_TO_ID_REGEX.fullmatch(filename)).groupdict()['id'])


class Feed:
    def __init__(self) -> None:
        log.info('The %s whitelisted research areas are: %s',
                 len(config.RESEARCH_AREAS), ', '.join(config.RESEARCH_AREAS))
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

        # Sort by ID
        pubs = [pub for pub in pubs if pub['filename_html']]
        for pub in pubs:
            pub[':id'] = filename_to_id(pub['filename_html'])
        pubs.sort(key=lambda pub: pub[':id'], reverse=True)

        # Create feed
        feed = self._init_feed()
        num_added = 0
        for pub in pubs:
            if num_added > config.MAX_ENTRIES:
                break

            is_research_area_whitelisted = not set(pub['tag_pks']).isdisjoint(self._areas)
            if not is_research_area_whitelisted:
                continue

            has_download_link = 'URL\t' in pub['bibtex']
            if not has_download_link:
                continue

            title = pub['title']
            url = config.PUB_URL_FORMAT.format(pub_id=pub[':id'])
            guid = str(pub[':id'])
            categories = pub['tag_pks']  # Often starts with "research-area-" or "team-".

            entry = feed.add_entry(order='append')
            entry.title(title)
            entry.link(href=url)
            entry.guid(guid, permalink=False)
            if 'abstract' in pub:
                desc = textwrap.shorten(pub['abstract'], float('inf'))  # type: ignore
                desc = ''.join(c for c in desc if c.isprintable())
                entry.description(desc)
            for category in categories:
                entry.category(term=category)

            log.debug('Added pub #%s having ID %s, title %s (%s), and categories: %s',
                      num_added + 1, pub[':id'], repr(title), pub['year'], ', '.join(c for c in categories))
            num_added += 1

        text: bytes = feed.rss_str(pretty=True)
        log.info('Output feed has %s items and size %s.', num_added, humanize_len(text))
        return text
