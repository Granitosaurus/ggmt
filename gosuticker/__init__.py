class Match(dict):
    keys = [
        'url',
        'id',
        'game',
        'time',
        'time_secs',
        't1',
        't1_country',
        't1_country_short',
        't2',
        't2_country',
        't2_country_short',
        'stream',
    ]

    def __setitem__(self, key, value):
        if key in self.keys:
            super().__setitem__(key, value)
        else:
            raise NotImplementedError('Unknown key {}'.format(key))

    def __setattr__(self, key, value):
        raise NotImplementedError("use Match['key'] to set attributes")


