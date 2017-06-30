import json
import os
import re
import subprocess
import sys
import webbrowser

import click
from jinja2 import Template
from requests.exceptions import ConnectionError

from ggmt import Match
from ggmt.tournament import LiquidBracketDownloader, EVENT_PAST, EVENT_FUTURE
from ggmt.matchticker import GosuTicker

COLOR_ENABLED = True
try:
    from colorama import Fore, Back
except ImportError:
    COLOR_ENABLED = False

DEFAULT_TEMPLATE = "{{t1}} vs {{t2}} in {{time}} {% if stream %}@ {{stream}}{% endif %}"
DEFAULT_TEMPLATE_ALL = "{{game}}: {{t1}} vs {{t2}} in {{time}} {% if stream %}@ {{stream}}{% endif %}"
DEFAULT_TEMPLATE_RECAP = "{{t1}} {{t1_score}}:{{t2_score}} {{t2}}"
HISTORY_LOCATION = os.path.expanduser('~/.ggmt_history')
with open(HISTORY_LOCATION, 'a') as f:  # make sure history file exists
    pass


def download_matches(game):
    """wrapper for connections errors that might be caused during match download"""
    try:
        matches = GosuTicker(game).download_matches()
    except ConnectionError:
        sys.exit('ERROR: No internet connection')
    except ConnectionRefusedError as e:
        sys.exit('Cannot connect to gosugamers: {}'.format(e.args[-1]))
    return matches


def download_history(game):
    """wrapper for connections errors that might be caused during match download"""
    try:
        matches = GosuTicker(game).download_history()
    except ConnectionError:
        sys.exit('ERROR: No internet connection')
    except ConnectionRefusedError as e:
        sys.exit('Cannot connect to gosugamers: {}'.format(e.args[-1]))
    return matches


def print_match(match, template):
    """wrapper to inject colorama colors to template"""
    click.echo(template.render(match, Fore=Fore, Back=Back))


def print_help_template(ctx, param, value):
    """prints help-template text"""
    if value:
        click.echo('Gosuticker is using Jinja2 templating engine to generate the displayed text.')
        click.echo('Default template for individual games:')
        click.secho('  {}'.format(DEFAULT_TEMPLATE), fg='green')
        click.echo('Default template for all:')
        click.secho('  {}'.format(DEFAULT_TEMPLATE_ALL), fg='green')
        click.echo('Template keys:')
        for k in Match.keys:
            click.echo('  {} - {}'.format(click.style(k, fg='green'), click.style(Match.keys[k], fg=None)))
        sys.exit()


@click.group()
@click.version_option()
@click.option('--help-template', help='Show help message for how to format template',
              is_flag=True, is_eager=True, expose_value=True, callback=print_help_template)
def cli(help_template):
    """Good Game Match Ticker - cli application for tracking match information for various esport games."""
    pass


@cli.command('tick', help='Show matchticker.')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.option('-t', '--template', help='set template')
@click.option('--json', 'is_json', help='output json', is_flag=True)
def tick(game, template, is_json):
    """Tick command is great"""
    if not game:
        raise click.BadParameter('Missing required parameter "game"')

    matches = download_matches(game)
    if is_json:
        click.echo(json.dumps(list(matches), indent=2, sort_keys=True))
        return
    template = template if template else DEFAULT_TEMPLATE_ALL if game == 'all' else DEFAULT_TEMPLATE
    template = Template(template)
    for m in matches:
        if COLOR_ENABLED and m['time_secs'] == 0:
            m['time'] = Fore.GREEN + m['time'] + Fore.RESET
        print_match(m, template)


@cli.command('recap', help='Show match history.')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.option('-nc', '--no-color', help='disable color being added', is_flag=True)
@click.option('-t', '--template', help='set template')
@click.option('--json', 'is_json', help='output json', is_flag=True)
def tick(game, template, is_json, no_color):
    if not game:
        raise click.BadParameter('Missing required parameter "game"')

    matches = download_history(game)
    if is_json:
        click.echo(json.dumps(list(matches), indent=2, sort_keys=True))
        return
    template = template if template else DEFAULT_TEMPLATE_RECAP
    template = Template(template)
    for m in matches:
        if no_color or not COLOR_ENABLED:  # if color is disabled just stdout
            print_match(m, template)
            continue
        if m['t1_score'] > m['t2_score']:
            m['t1'] = Fore.GREEN + m['t1'] + Fore.RESET
            m['t2'] = Fore.RED + m['t2'] + Fore.RESET
        else:
            m['t2'] = Fore.GREEN + m['t2'] + Fore.RESET
            m['t1'] = Fore.RED + m['t1'] + Fore.RESET
        print_match(m, template)


@cli.command('watch', help='Open a stream in browser or media player(via streamlink).')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.option('-s', '--show-unavailable', 'show', is_flag=True,
              help="list matches that don't have streams too")
@click.option('-t', '--template',
              help='set message template')
@click.option('-w', '--in-window', is_flag=True,
              help='open stream in window instead of tab(if possible)')
@click.option('-l', '--use-streamlink', is_flag=True,
              help='open using streamlink instead, requires: https://github.com/streamlink/streamlink')
@click.option('-p', '--print', 'just_print', is_flag=True, help='just print url instead')
@click.option('-q', '--quality', help='[default:best] quality when using streamlink', default='best')
def watch(game, show, template, in_window, use_streamlink, quality, just_print):
    matches = list(download_matches(game))
    if not show:
        matches = [m for m in matches if m.get('stream')]
    if not matches:
        click.echo('No streams found :(')
        return

    template = template if template else DEFAULT_TEMPLATE_ALL if game == 'all' else DEFAULT_TEMPLATE
    template = Template(template)
    items = ['{}: {}'.format(i, template.render(m)) for i, m in enumerate(matches)]
    for item in items:
        click.echo(item)
    click.echo('-' * len(sorted(items)[0]))
    while True:
        click.echo('select stream to show: ', nl=False)
        choice = input('')
        if not choice.isdigit():
            click.echo('  "{}" is not a number'.format(choice))
            continue
        choice = int(choice)
        if choice not in range(0, len(matches)):
            click.echo('  {} is out of range'.format(choice))
            continue
        break

    selected = matches[choice].get('stream')
    if not selected:
        click.secho('cannot stream for match #{}: no stream'.format(choice), err=True, fg='red')
        return

    if just_print:
        click.echo(selected)
        return
    click.echo('Opening {}...'.format(selected))
    if use_streamlink:
        subprocess.Popen(['nohup streamlink "{}" {} &'.format(selected, quality)], shell=True, start_new_session=True)
    elif not in_window:
        webbrowser.open_new_tab(selected)
    else:
        webbrowser.open(selected, new=1)


@cli.command('notify', help='Notify if a specific team plays.')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.argument('team')
@click.option('-f', '--force', is_flag=True,
              help='ignore history')
@click.option('-s', '--seconds', default=900,
              help='seconds threshold before sending out the notification (default=900)')
@click.option('-m', '--minutes', default=0,
              help='minutes threshold before sending out the notification (default=15)')
@click.option('-p', '--pushbullet', is_flag=True,
              help='Use pushbullet notification instead system notify-send')
@click.option('-k', '--pushbullet-key', help='Pushbullet API key to use to send the notification, '
                                             'can be set through enviroment variable PUSHBULLET_API')
def notify(game, team, seconds, minutes, pushbullet, pushbullet_key, force):
    team = team.lower().strip()
    if pushbullet:
        if not pushbullet_key:
            pushbullet_key = os.environ.get('PUSHBULLET_API', '')
        if not pushbullet_key:
            click.secho('To use pushbullet notification supply --pushbulet-key '
                        'or enviroment variable PUSHBULLET_API', err=True, fg='red')
            return
        try:
            from pushbullet import Pushbullet
        except ImportError:
            click.secho('To use pushbullet notification install pusbullet.py package;'
                        ' pip install pushbullet.py', err=True, fg='red')
            return

    if minutes:
        seconds = minutes * 60
    matches = download_matches(game)
    re_team = re.compile(team, flags=re.I)
    for match in matches:
        if int(match['time_secs']) > int(seconds):
            continue
        if re_team.match(match['t1']) or re_team.match(match['t2']):
            # already in history?
            if not force:
                with open(HISTORY_LOCATION, 'r') as f:
                    if match.id in f.read():
                        continue
            # notify
            title = "{} vs {} in {}".format(match['t1'], match['t2'], match['time'])
            body = match.get('stream') or match['url']
            if pushbullet:
                push = Pushbullet(pushbullet_key)
                push.push_note(title, body)
            else:
                # The if check below is for fixing notify-send to work with cron
                # cron notify-send requires $DBUS_SESSION_BUS_ADDRESS to be set
                # as per http://unix.stackexchange.com/questions/111188
                subprocess.call('if [ -r "$HOME/.dbus/Xdbus" ]; '
                                'then . $HOME/.dbus/Xdbus; '
                                'fi && notify-send "{}" "{}"'.format(title, body),
                                shell=True)
            # add to history
            with open(HISTORY_LOCATION, 'a') as f:
                f.write('{}\n'.format(match.id))


@cli.command('tournament', help='display tournament brackets, default: current tournaments')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.option('-p', '--past', help='show past tournaments', is_flag=True)
@click.option('-a', '--all', 'all_', help='show all tournaments', is_flag=True)
@click.option('-f', '--future', help='show future tournaments', is_flag=True)
@click.option('-b', '--bracket', help='show brackets (experimental)', is_flag=True)
@click.option('-j', '--json', 'as_json', help='output json', is_flag=True)
def tournament(game, past, future, bracket, as_json, all_):
    dl = LiquidBracketDownloader(game)
    if all_:
        events = dl.find_tournaments(EVENT_PAST)
        events.extend(dl.find_tournaments())
        events.extend(dl.find_tournaments(EVENT_FUTURE))
    else:
        cat = EVENT_PAST if past else None
        cat = EVENT_FUTURE if future else cat
        events = dl.find_tournaments(category=cat)
    if as_json:
        click.echo(json.dumps(events, indent=2))
        return
    if not events:
        click.echo('No events found :(')
        return
    max_len = len(sorted([e['name'] for e in events], key=lambda s: len(s), reverse=True)[0])
    longest = 0
    for i, event in enumerate(events):
        text = '{}: {} | {}'.format(i, event['name'].ljust(max_len), event['date'])
        if not bracket:
            text = text.split(': ', 1)[1]
        if len(text) > longest:
            longest = len(text)
        click.echo(text)
        click.echo('    {}'.format(event['url']))
    if not bracket:
        return
    click.echo('-' * longest)
    while True:
        click.echo('select tournament to display: ', nl=False)
        choice = input('')
        if not choice.isdigit():
            click.echo('  "{}" is not a number'.format(choice))
            continue
        choice = int(choice)
        if choice not in range(0, len(events)):
            click.echo('  {} is out of range'.format(choice))
            continue
        break
    brackets = dl.download_brackets(events[choice].url)
    for bracket in brackets:
        click.echo(bracket.to_text())
