from collections import OrderedDict


class StrictDict(dict):
    keys = []
    keys = OrderedDict(keys)

    def __setitem__(self, key, value):
        if key in self.keys:
            super().__setitem__(key, value)
        else:
            raise NotImplementedError('Unknown key {}'.format(key))

    def __setattr__(self, key, value):
        raise NotImplementedError("use {}['key'] to set attributes".format(self.__name__))


class Match(StrictDict):
    """
    Storage object for storing esport games match data.
    See Match.keys for available keys
    """
    keys = [
        ('url', 'url to gosugamers match page'),
        ('id', 'gosugamers match id'),
        ('game', 'game name'),
        ('time', 'time in text as displayed on gosugamers'),
        ('time_secs', 'time in integer seconds'),
        ('timestamp', 'UNIX timestamp of when the game is starting'),
        ('t1', 'name of team 1'),
        ('t1_country', 'country of team 1'),
        ('t1_country_short', 'short version of country of team 1'),
        ('t1_score', 'score of team 1'),
        ('t2', 'cname of team 2'),
        ('t2_country', 'country of team 2'),
        ('t2_country_short', 'short version of country of team 2'),
        ('t2_score', 'score of team 2'),
        ('stream', 'direct stream url to match hosting channel'),
    ]
    keys = OrderedDict(keys)

    @property
    def id(self):
        return "{}_{}_{}".format(self['id'], self['t1'], self['t2'])


class Event(StrictDict):
    keys = [
        ('name', 'tournament name'),
        ('date', 'when tournament was on going'),
        ('url', 'url to liquidpedia page'),
        ('info', 'information about tournament'),
    ]
    keys = OrderedDict(keys)
