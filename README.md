# Good Game Match Ticker

[![PyPi version](https://img.shields.io/pypi/v/ggmt.svg?style=flat-square)](https://pypi.python.org/pypi/ggmt)
[![PyPi license](https://img.shields.io/pypi/l/ggmt.svg?style=flat-square)](https://pypi.python.org/pypi/ggmt)
[![PyPi license](https://img.shields.io/pypi/pyversions/ggmt.svg?style=flat-square)](https://pypi.python.org/pypi/ggmt)   

ggmt is a match ticker command line application for linux that can:
  * Show live and upcoming esport matches.
  * Notify when matches are about to start. 
  * Open up streams of ongoing matches.
  * Show recap/results of latest matches
  
It's designed with templating in mind so it can be used to produce match tickers for your applications or websites.  

    Usage: ggmt [OPTIONS] COMMAND [ARGS]...
      Good Game Match Ticker - cli application for tracking match information
      for various esport games.

    Options:
      --version        Show the version and exit.
      --help-template  Show help message for how to format template
      --help           Show this message and exit.

    Commands:
      list    List supported games.
      notify  Notify if a specific team plays.
      recap   Show match history.
      tick    Show matchticker.
      watch   Open a stream in browser or media player(via streamlink).

Screenshots:  

![preview](https://github.com/Granitosaurus/ggmt/raw/master/screenshot.png)

ggmt is also based on jinja2 templates, so the data can be easily customized to display in your format for your website or application.

```console
Usage: ggmt [OPTIONS] COMMAND [ARGS]...
Commands:
  list    list support games
  notify  notify if a specific team plays
  tick    display matchticker
```

## Install

Via pip:

```console
pip install ggmt
# or
pip istall git+https://github.com/Granitas/ggmt.git
```

Or 

```console
git clone https://github.com/Granitas/ggmt.git
cd ggmt
python3 setup.py install
```

## Commands

### Ticker  

```
Show matchticker.  
Options:  
  -t, --template TEXT  set template  
  --json               output json  
  --help               Show this message and exit.  
```

Matchticker that prints out upcoming/ongoing match data. Prints data to stdout in text or json. Text can be customized by using jinja2 templates.

*examples:*  
Simply supply game name as first argument

```console
$ ggmt tick dota2
DUOBAO vs Taring in Live
NGE vs AcA in Live
El_one vs TBE in 3m 38s
Elements. vs Sweet. in 1w 2h
```

You can use a full custom jinja2 template (see --help-template for template keys)

```console
$ ggmt tick dota2 --template "{{t1_country_short}} vs {{t2_country}} in {{time_secs/60}} minutes"
RS vs Europe in 0.0 minutes
RU vs Russian Federation in 0.0 minutes
CN vs Malaysia in 0.0 minutes
VN vs Philippines in 0.0 minutes
KG vs Poland in 89.0 minutes
RO vs Poland in 179.0 minutes
```


### Notifier

```
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
```

Notify when a match with a specific team playing is about to start using system-notify or [pushbullet][pushbullet] service. Argument `team` is a case insensitive regular expressions fielda.  
**_Important_**: notification history is stored in `~/.ggmt_history` to prevent flooding. You can ignore history with a -f/--force flag

Example:

Notify 30 minutes before game starts
```console
$ ggmt notify dota2 na`vi --minutes 30
```

Notify via pushbullet when live
```console
$ export PUSHBULLET_API=<api_key>
$ ggmt notify dota2 na`vi --seconds 0 --pushbullet
```

#### Using With Cron

Of course notifier is only useful if it is checking constantly. To do that you can use cron services via `crontab -e` command on linux, add this crontab: 

```cron
*/10 * * * * /usr/bin/ggmt notify dota2 na`vi --minutes 5
```

This will check for na'vi games every 10 minutes.

**Important:**
To use `notify-send` with cron you need to apply fix described in [this issue](http://unix.stackexchange.com/a/111190/73477). In short you need to expose your `DBUS_SESSION_BUS_ADDRESS` to `$HOME/.dbus/Xdbus` file.   
If anyone knows workaround for this please submit and issue or a PR!


### Watch

```
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
```

This command shows you a list of available streams and opens up a selected one in your browser or default mediaplayer (via use of [sreamlink][streamlink])

Example:
```console
    $ ggmt watch dota2
    0: CDEC vs FTD.C in Live @ http://twitch.tv/esl_joindotablue
    1: Na'vi vs Alliance in Live @ http://twitch.tv/justkidding
    ------------------------------------------------------------
    Enter number of stream to open: 0
    Opening http://twitch.tv/esl_joindotablue...
```


[streamlink]: https://github.com/streamlink/streamlink
[pushbullet]: https://www.pushbullet.com/
