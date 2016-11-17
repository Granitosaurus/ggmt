import json
import os
import re
import subprocess
import sys
import webbrowser

import click
from jinja2 import Template
from requests.exceptions import ConnectionError

from gosuticker import Match
from gosuticker.matchticker import GosuTicker

DEFAULT_TEMPLATE = "{{t1}} vs {{t2}} in {{time}} {% if stream %}@ {{stream}}{% endif %}"
DEFAULT_TEMPLATE_ALL = "{{game}}: {{t1}} vs {{t2}} in {{time}} {% if stream %}@ {{stream}}{% endif %}"
HISTORY_LOCATION = os.path.expanduser('~/.gosuticker_history')
with open(HISTORY_LOCATION, 'a') as f:  # make sure history file exists
    pass


def download_matches(game):
    """little wrapper for connections errors that might be caused during match download"""
    try:
        matches = GosuTicker(game).download_matches()
    except ConnectionError:
        sys.exit('ERROR: No internet connection')
    except ConnectionRefusedError as e:
        sys.exit('Cannot connect to gosugamers: {}'.format(e.args[-1]))
    return matches


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
    pass


@cli.command('list', help='list support games')
def list_games():
    for game in GosuTicker.games:
        click.echo(game)


@cli.command('tick', help='Show matchticker.')
@click.argument('game', type=click.Choice(GosuTicker.games))
@click.option('-t', '--template', help='set template')
@click.option('--json', 'is_json', help='output json', is_flag=True)
def tick(game, template, is_json):
    if not game:
        raise click.BadParameter('Missing required parameter "game"')

    matches = download_matches(game)
    if is_json:
        click.echo(json.dumps(list(matches), indent=2, sort_keys=True))
        return
    template = template if template else DEFAULT_TEMPLATE_ALL if game == 'all' else DEFAULT_TEMPLATE
    template = Template(template)
    for m in matches:
        click.echo(template.render(m))


@cli.command('watch', help='Open a stream in browser or media player.')
@click.argument('game')
@click.option('-s', '--show-unavailable', 'show', is_flag=True,
              help="list matches that don't have streams too")
@click.option('-t', '--template',
              help='set message template')
@click.option('-w', '--in-window', is_flag=True,
              help='open stream in window instead of tab(if possible)')
@click.option('-l', '--use-streamlink', is_flag=True,
              help='open sing streamlink instead, requires: https://github.com/streamlink/streamlink')
@click.option('-p', '--print', 'just_print', is_flag=True, help='just print url instread')
@click.option('-q', '--quality', help='[default:best] open in livestreamer instead', default='best')
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
        choice = input('Enter number of stream to open: ')
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
        subprocess.Popen(['streamlink "{}" {}'.format(selected, quality)], shell=True)
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
                    if match['id'] in f.read():
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
                f.write('{}\n'.format(match['id']))
