# Gosuticker
Is a template-based matchticker based on data displayed on gosugamers.com website

```console
$ gosuticker --help
Usage: gosuticker [OPTIONS] [GAME]

Options:
  --version            Show the version and exit.
  -t, --template TEXT  set template
  --list-games         list supported games
  --help-template      print help message for how to format template
  --help               Show this message and exit.
```

### Install

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

### Examples

Simply supply game name as first argument

```console
$ gosuticker dota2
DUOBAO vs Taring in Live
NGE vs AcA in Live
El_one vs TBE in 3m 38s
Elements. vs Sweet. in 1w 2h
```

You can use a full custom jinja2 template (see --help-template for template keys)

```console
$ gosuticker dota2 --template "{{opp1_country_short}} vs {{opp2_country}} in {{time_secs/60}} minutes"
RS vs Europe in 0.0 minutes
RU vs Russian Federation in 0.0 minutes
CN vs Malaysia in 0.0 minutes
VN vs Philippines in 0.0 minutes
KG vs Poland in 89.0 minutes
RO vs Poland in 179.0 minutes
```


### Use cases

You can build a simple notifier:

```
notify-send "$(gosuticker dota2 | grep -i 'secret')"  
```


