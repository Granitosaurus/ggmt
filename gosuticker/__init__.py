from collections import OrderedDict


class Match(dict):
    keys = [
        ('url', 'url to gosugamers match page'),
        ('id', 'gosugamers match id'),
        ('game', 'game name'),
        ('time', 'time in text as displayed on gosugamers'),
        ('time_secs', 'time in integer seconds'),
        ('t1', 'name of team 1'),
        ('t1_country', 'country of team 1'),
        ('t1_country_short', 'short version of country of team 1'),
        ('t2', 'cname of team 2'),
        ('t2_country', 'country of team 2'),
        ('t2_country_short', 'short version of country of team 2'),
        ('stream', 'direct stream url to match hosting channel'),
    ]
    keys = OrderedDict(keys)

    def __setitem__(self, key, value):
        if key in self.keys:
            super().__setitem__(key, value)
        else:
            raise NotImplementedError('Unknown key {}'.format(key))

    def __setattr__(self, key, value):
        raise NotImplementedError("use Match['key'] to set attributes")


