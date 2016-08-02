# Gosuticker
Is a template-based matchticker based on data displayed on gosugamers.com website

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
-----------------------------------------------------------------------

### Ticker  

Matchticker that prints out upcoming/ongoing match data. Prints data to stdout in template-customizable text or json

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
$ gosuticker tick dota2 --template "{{opp1_country_short}} vs {{opp2_country}} in {{time_secs/60}} minutes"
RS vs Europe in 0.0 minutes
RU vs Russian Federation in 0.0 minutes
CN vs Malaysia in 0.0 minutes
VN vs Philippines in 0.0 minutes
KG vs Poland in 89.0 minutes
RO vs Poland in 179.0 minutes
```


### Notifier

Notify when a match with a specific team playing is about to start using system notify or pushbullet service.  
**_Important_**: notification history is stored in `~/.gosuticker_history` to prevent flooding.

Notify 30 minutes before game starts
```console
$ gosuticker notify dota2 na`vi --minutes 30
```

Notify via pushbullet when live
```console
$ export PUSHBULLET_API=<api_key>
$ gosuticker notify dota2 na`vi --seconds 0 --pushbullet
```

