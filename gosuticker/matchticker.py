import re
from urllib.parse import urljoin

import requests
from parsel import Selector

from gosuticker import Match


def parse_time(text):
    """converts text time to seconds"""
    if 'live' in text.lower():
        return 0
    text = text.strip().lower()
    seconds = 0
    seconds += int((re.findall('(\d+)h', text) or [0])[0]) * 3600
    seconds += int((re.findall('(\d+)m', text) or [0])[0]) * 60
    return seconds


class GosuTicker:
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

    def __init__(self, game):
        if game not in self.games:
            raise NotImplementedError(""""parser for game "{}" doesn't exist""".format(game))
        if game == 'all':
            game = ''
        self.game_url = self.url_base + game

    def download_matches(self):
        resp = requests.get(self.game_url)
        sel = Selector(text=resp.text)
        return self.find_matches(sel)

    def find_matches(self, sel):
        matches = sel.xpath("//table[@id='gb-matches']//tr")
        for match in matches:
            xpath = lambda x: match.xpath(x).extract_first(default='').strip()
            item = Match()
            item['url'] = urljoin(self.url_base, xpath(".//a/@href"))
            item['id'] = (re.findall('matches/(\d+)', item['url']) or [None])[0]
            item['game'] = next((g for g in self.games if g in item['url'].lower()))
            item['time'] = xpath("td[@class='status']/span/text()")
            item['time_secs'] = parse_time(item['time'])
            item['opp1'] = xpath(".//span[contains(@class,'opp1')]/span/text()")
            item['opp1_country'] = xpath(".//span[contains(@class,'opp1')]/span[contains(@class,'flag')]/@title")
            item['opp1_country_short'] = xpath(".//span[contains(@class,'opp1')]"
                                               "/span[contains(@class,'flag')]/@class").split()[-1]
            item['opp2'] = xpath(".//span[contains(@class,'opp2')]/span/text()")
            item['opp2_country'] = xpath(".//span[contains(@class,'opp2')]/span[contains(@class,'flag')]/@title")
            item['opp2_country_short'] = xpath(".//span[contains(@class,'opp2')]"
                                               "/span[contains(@class,'flag')]/@class").split()[-1]
            yield item
