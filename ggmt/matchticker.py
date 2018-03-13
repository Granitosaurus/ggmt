import logging
import re
from datetime import timedelta, datetime
from typing import Generator, List
from urllib.parse import urljoin

import requests
from parsel import Selector

from ggmt import Match


def parse_time(text):
    """
    converts text time to seconds
    :returns: seconds integer
    """
    if 'live' in text.lower():
        return 0
    text = text.strip().lower()
    seconds = 0
    seconds += int((re.findall('(\d+)w', text) or [0])[0]) * 3600 * 24 * 7
    seconds += int((re.findall('(\d+)d', text) or [0])[0]) * 3600 * 24
    seconds += int((re.findall('(\d+)h', text) or [0])[0]) * 3600
    seconds += int((re.findall('(\d+)m', text) or [0])[0]) * 60
    return seconds


def clean_stream_url(url):
    """
    Converts various stream embed urls to normal channel urls.
    :param url: dirty embed url
    :returns: clean channel url
    """
    if not url:
        return url
    if 'twitch' in url and 'channel=' in url:
        channel = re.findall('channel=(.+?)(?:&|$)', url)
        if not channel:
            logging.error("Couldn't clean stream url: {}".format(url))
            return url
        return 'http://twitch.tv/' + channel[0]

    url = url.split('?', 1)[0]
    url = url.replace('#!/embed/', '')
    url = url.replace('//embed.', '//')
    return url


class GosuTicker:
    """
    Match downloader for http://gosugamers.net source
    """
    games = [
        'dota2',
        'counterstrike',
        'hearthstone',
        'heroesofthestorm',
        'lol',
        'overwatch',
        'starcraft2',
        'all',
    ]
    url_base = "http://www.gosugamers.net/"
    logger = logging.getLogger('gosuticker')

    def __init__(self, game):
        if game not in self.games:
            raise NotImplementedError(""""parser for game "{}" doesn't exist""".format(game))
        if game == 'all':
            game = ''
        self.game_url = self.url_base + game
        self.session = requests.session()

    def download_matches(self, crawl_stream: bool = True) -> List[Match]:
        """
        Downloads live and upcoming matches.
        :return: list of eticker.Match objects
        """
        resp = self.session.get(self.game_url)
        if resp.status_code != 200:
            raise ConnectionRefusedError('Got response error {}'.format(resp.status_code))
        sel = Selector(text=resp.text)
        matches = list(self.find_matches(sel))
        if crawl_stream:
            matches = self.update_match_streams(matches)
        return matches

    def download_history(self, crawl_stream: bool = True) -> List[Match]:
        """
        Downloads recent matches.
        :return: list of eticker.Match objects
        """
        resp = self.session.get('{}/gosubet'.format(self.game_url))
        if resp.status_code != 200:
            raise ConnectionRefusedError('Got response error {}'.format(resp.status_code))
        sel = Selector(text=resp.text)
        matches = list(self.find_history(sel))
        if crawl_stream:
            matches = self.update_match_streams(matches)
        return matches

    def _find_match(self, sel: Selector) -> Match:
        xpath = lambda x: sel.xpath(x).extract_first(default='').strip()
        item = Match()
        item['url'] = urljoin(self.url_base, xpath(".//a/@href"))
        item['id'] = (re.findall('matches/(\d+)', item['url']) or [None])[0]
        item['game'] = next((g for g in self.games if g in item['url'].lower()))
        item['time'] = xpath("td[@class='status']/span/text()")
        item['time_secs'] = parse_time(item['time'])
        item['timestamp'] = int((datetime.now() + timedelta(item['time_secs'])).timestamp())
        item['t1'] = xpath(".//span[contains(@class,'opp1')]/span/text()")
        item['t1_country'] = xpath(".//span[contains(@class,'opp1')]/span[contains(@class,'flag')]/@title")
        item['t1_country_short'] = xpath(".//span[contains(@class,'opp1')]"
                                         "/span[contains(@class,'flag')]/@class").split()[-1]
        item['t2'] = xpath(".//span[contains(@class,'opp2')]/span/text()")
        item['t2_country'] = xpath(".//span[contains(@class,'opp2')]/span[contains(@class,'flag')]/@title")
        item['t2_country_short'] = xpath(".//span[contains(@class,'opp2')]"
                                         "/span[contains(@class,'flag')]/@class").split()[-1]
        scores = sel.css('.score::text').extract()
        item['t1_score'] = scores[0] if scores else None
        item['t2_score'] = scores[1] if len(scores) > 1 else None
        return item

    def update_match_streams(self, matches: List[Match]) -> List[Match]:
        """Populate Match objects with stream urls"""
        updated = []
        for item in matches:
            # Populate stream data if match is live
            if not item['time_secs']:
                resp = self.session.get(item['url'])
                sel_detailed = Selector(text=resp.text)
                item['stream'] = sel_detailed.xpath("//div[@class='matches-streams']"
                                                    "/span[.//a[re:test(text(),'english', 'i')]]"
                                                    "//iframe/@src").extract_first()
                item['stream'] = clean_stream_url(item['stream'])
            updated.append(item)
        return updated

    def find_matches(self, sel: Selector) -> Generator[Match, None, None]:
        """
        Generator to find live and upcoming matches in parsel.Selector object
        :returns: yields eticker.Match objects
        """
        matches = sel.xpath("//table[@id='gb-matches']//tr")
        for match in matches:
            item = self._find_match(match)
            yield item

    def find_history(self, sel: Selector) -> Generator[Match, None, None]:
        """
        Generator to find recent matches in parsel.Selector object
        :returns: yields eticker.Match objects
        """
        matches = sel.xpath("//h2[contains(text(),'Recent')]/..//tr")
        for match in matches:
            item = self._find_match(match)
            yield item

