class Match(dict):
    keys = [
        'url',
        'id',
        'game',
        'time',
        'time_secs',
        'opp1',
        'opp1_country',
        'opp1_country_short',
        'opp2',
        'opp2_country',
        'opp2_country_short',
    ]

    def __setitem__(self, key, value):
        if key in self.keys:
            super().__setitem__(key, value)
        else:
            raise NotImplementedError('Unknown key {}'.format(key))

    def __setattr__(self, key, value):
        raise NotImplementedError("use Match['key'] to set attributes")


