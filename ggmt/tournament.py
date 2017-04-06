from urllib.parse import urljoin

import requests
import sys
from parsel.selector import Selector

from ggmt import Event

EVENT_CURRENT = 'Ongoing'
EVENT_PAST = 'Completed'
EVENT_FUTURE = 'Upcoming'


class LiquidBracketDownloader:
    """Bracket downloader for brackets displayed on LiquidPedia"""
    games = [
        'dota2',
        'counterstrike',
        # 'hearthstone',
        # 'heroesofthestorm',
        'overwatch',
        # 'starcraft2',
        # 'all',
    ]
    url_base = 'http://wiki.teamliquid.net/'

    def __init__(self, game):
        if game not in self.games:
            raise NotImplementedError(""""parser for game "{}" doesn't exist""".format(game))
        if game == 'all':
            game = ''
        self.game_url = self.url_base + game

    def find_tournaments(self, category=None):
        """
        :param category: what category to show,
            choice from: EVENT_CURRENT[default], EVENT_PAST, EVENT_FUTURE
        :return: list of Events
        """
        if category is None:
            category = EVENT_CURRENT
        resp = requests.get(self.game_url)
        sel = Selector(text=resp.text)
        ongoing_events = sel.xpath("//li[contains(text(),'{}')]/..//a".format(category))
        if not ongoing_events:
            ongoing_events = sel.xpath("//div[contains(text(),'COMPLETED')]"
                                       "/following-sibling::div/a")
        ongoing = []
        for t in ongoing_events:
            event = Event()
            event['name'] = t.xpath('text()').extract_first('')
            event['date'] = t.xpath('small/text()').extract_first('').strip('()')
            event['url'] = urljoin(self.url_base, t.xpath('@href').extract_first(''))
            resp = requests.get(event['url'])
            sel = Selector(text=resp.text)
            info = sel.xpath("//div[contains(@class,'infobox-header')][contains(text(), 'League Info')]/../..")
            event['info'] = dict()
            for node in info.xpath("//div[contains(@class,'infobox-description')]"):
                title = node.xpath('text()').extract_first('').lower().strip(':')
                value = ''.join(node.xpath('following-sibling::div//text()').extract()).strip()
                url = node.xpath('following-sibling::div/a/@href').extract_first('')
                event['info'][title] = {'value': value, 'url': urljoin(self.url_base, url)} if url else value
            ongoing.append(event)
        return ongoing

    def download_brackets(self, url):
        """
        Experimental
        Download and display brackets in the terminal
        """
        try:
            from terminalbrackets import Team, Bracket
        except ImportError:
            sys.exit('For brackets functionality "terminalbrackets" package is required')
        resp = requests.get(url)
        sel = Selector(text=resp.text)

        brackets = sel.css('.bracket-scroller')
        xtr_brackets = []
        for bracket in brackets:
            bracket_name = ''.join(bracket.xpath('../preceding-sibling::h3[1]//text()').extract())

            rounds = bracket.css('.bracket-column-matches')
            xtr_rounds = []
            for r in rounds:
                teams = r.xpath('.//div[contains(@class,"bracket-cell")]')
                xtr_teams = []
                for t in teams:
                    name = t.css('.team-template-team-bracket span::text').extract_first('')
                    score = t.css('.bracket-score::text').extract_first(0)
                    if name and score:
                        xtr_teams.append(Team(name, score))
                xtr_rounds.append(xtr_teams)
            xtr_brackets.append(Bracket(bracket_name, xtr_rounds))
        print(xtr_brackets)
        return xtr_brackets

