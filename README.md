# Gosuticker

[![PyPi version](https://img.shields.io/pypi/v/gosuticker.svg?style=flat-square)](https://pypi.python.org/pypi/gosuticker)
[![PyPi license](https://img.shields.io/pypi/l/gosuticker.svg?style=flat-square)](https://pypi.python.org/pypi/gosuticker)
[![PyPi license](https://img.shields.io/pypi/pyversions/gosuticker.svg?style=flat-square)](https://pypi.python.org/pypi/gosuticker)   
A template-based matchticker based on data displayed on gosugamers.com website

```console
Usage: gosuticker [OPTIONS] COMMAND [ARGS]...
Commands:
  list    list support games
  notify  notify if a specific team plays
  tick    display matchticker
```

## Install

Via pip:

```console
pip install gosuticker
# or
pip istall git+https://github.com/Granitas/gosuticker.git
```

Or 

```console
git clone https://github.com/Granitas/gosuticker.git
cd gosuticker
python3 setup.py install
```

## Commands

### Ticker  

Matchticker that prints out upcoming/ongoing match data. Prints data to stdout in text or json. Text can be customized by using jinja2 templates.

*examples:*  
Simply supply game name as first argument

```console
$ gosuticker tick dota2
DUOBAO vs Taring in Live
NGE vs AcA in Live
El_one vs TBE in 3m 38s
Elements. vs Sweet. in 1w 2h
```

You can use a full custom jinja2 template (see --help-template for template keys)

```console
$ gosuticker tick dota2 --template "{{t1_country_short}} vs {{t2_country}} in {{time_secs/60}} minutes"
RS vs Europe in 0.0 minutes
RU vs Russian Federation in 0.0 minutes
CN vs Malaysia in 0.0 minutes
VN vs Philippines in 0.0 minutes
KG vs Poland in 89.0 minutes
RO vs Poland in 179.0 minutes
```


### Notifier
Notify if a specific team plays.
Options:
  -f, --force                ignore history
  -s, --seconds INTEGER      seconds threshold before sending out the
                             notification (default=900)
  -m, --minutes INTEGER      minutes threshold before sending out the
                             notification (default=15)
  -p, --pushbullet           Use pushbullet notification instead system
                             notify-send
  -k, --pushbullet-key TEXT  Pushbullet API key to use to send the
                             notification, can be set through enviroment
                             variable PUSHBULLET_API
  --help                     Show this message and exit.

Notify when a match with a specific team playing is about to start using system-notify or [pushbullet][pushbullet] service. Argument `team` is a case insensitive regular expressions fielda.  
**_Important_**: notification history is stored in `~/.gosuticker_history` to prevent flooding. You can ignore history with a -f/--force flag

Example:

Notify 30 minutes before game starts
```console
$ gosuticker notify dota2 na`vi --minutes 30
```

Notify via pushbullet when live
```console
$ export PUSHBULLET_API=<api_key>
$ gosuticker notify dota2 na`vi --seconds 0 --pushbullet
```

#### Using With Cron

Of course notifier is only useful if it is checking constantly. To do that you can use cron services via `crontab -e` command on linux, add this crontab: 

```cron
*/10 * * * * /usr/bin/gosuticker notify dota2 na`vi --minutes 5
```

This will check for na'vi games every 10 minutes.

**Important:**
To use `notify-send` with cron you need to apply fix described in [this issue](http://unix.stackexchange.com/a/111190/73477). In short you need to expose your `DBUS_SESSION_BUS_ADDRESS` to `$HOME/.dbus/Xdbus` file.   
If anyone knows workaround for this please submit and issue or a PR!


### Watch

Open a stream in browser or media player.
Options:
  -s, --show-unavailable  list matches that don't have streams too
  -t, --template TEXT     set message template
  -w, --in-window         open stream in window instead of tab(if possible)
  -l, --use-streamlink    open sing streamlink instead, requires:
                          https://github.com/streamlink/streamlink
  -p, --print             just print url instread
  -q, --quality TEXT      [default:best] open in livestreamer instead
  --help                  Show this message and exit.


This command shows you a list of available streams and opens up a selected one in your browser or default mediaplayer (via use of [sreamlink][streamlink])

Example:
```console
    $ gosuticker watch dota2
    0: CDEC vs FTD.C in Live @ http://twitch.tv/esl_joindotablue
    1: Na'vi vs Alliance in Live @ http://twitch.tv/justkidding
    ------------------------------------------------------------
    Enter number of stream to open: 0
    Opening http://twitch.tv/esl_joindotablue...
```


[streamlink]: https://github.com/streamlink/streamlink
[pushbullet]: https://www.pushbullet.com/
