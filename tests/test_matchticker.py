import json

import pkg_resources

import requests
from parsel import Selector

from ggmt.matchticker import GosuTicker


class TestMatchTicker:
    def test_matches(self):
        for game in GosuTicker.games:
            self._test_match(game)

    def _test_match(self, game):
        gt = GosuTicker(game)
        data = pkg_resources.resource_string('tests', f'/html/match_{game}.html').decode('utf-8')
        result = pkg_resources.resource_string('tests', f'/html/match_{game}.json').decode('utf-8')
        sel = Selector(text=data)
        matches = list(gt.find_matches(sel))
        assert json.dumps(matches) == result

    def _save_matches(self):
        for game in GosuTicker.games:
            print('updating test data for: {}'.format(game))
            gt = GosuTicker(game)
            data = requests.get(gt.game_url).text
            sel = Selector(text=data)
            matches = list(gt.find_matches(sel))
            with open(f'html/match_{game}.html', 'w') as f:
                f.write(data)
            with open(f'html/match_{game}.json', 'w') as f:
                f.write(json.dumps(matches))


if __name__ == '__main__':
    t = TestMatchTicker()
    t._save_matches()
