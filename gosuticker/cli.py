import json
import os
import re
import subprocess
import sys

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


@click.group()
@click.version_option()
def cli():
    pass


@cli.command('list', help='list support games')
def list_games():
    for game in GosuTicker.games:
        click.echo(game)


@cli.command('tick', help='display matchticker')
@click.argument('game', required=False)
@click.option('-t', '--template', help='set template')
@click.option('--json', 'is_json', help='output json', is_flag=True)
@click.option('--help-template', help='print help message for how to format template', is_flag=True)
def tick(game, template, help_template, is_json):
    if help_template:
        click.echo('Gosuticker is using Jinja2 templating engine')
        click.echo('default template for individual games: "{}"'.format(DEFAULT_TEMPLATE))
        click.echo('default template for all: "{}"'.format(DEFAULT_TEMPLATE_ALL))
        click.echo('template keys:')
        for k in Match.keys:
            click.echo('    {}'.format(k))
        return
    if not game:
        raise click.BadParameter('Missing required parameter "game"')
    if game not in GosuTicker.games:
        click.echo('Unknown game "{}", see "gosuticker list" for game list'.format(game), err=True)
        return
    try:
        matches = GosuTicker(game).download_matches()
    except ConnectionError:
        sys.exit('ERROR: No internet connection')
    if is_json:
        click.echo(json.dumps(list(matches), indent=2, sort_keys=True))
        return
    template = template if template else DEFAULT_TEMPLATE_ALL if game == 'all' else DEFAULT_TEMPLATE
    template = Template(template)
    for m in matches:
        click.echo(template.render(m))


@cli.command('notify', help='notify if a specific team plays')
@click.argument('game')
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
            click.echo('To use pushbullet notification supply --pushbulet-key '
                       'or enviroment variable PUSHBULLET_API', err=True)
            return
        try:
            from pushbullet import Pushbullet
        except ImportError:
            click.echo('To use pushbullet notification install pusbullet.py package;'
                       ' pip install pushbullet.py', err=True)
            return

    if minutes:
        seconds = minutes * 60
    try:
        matches = GosuTicker(game).download_matches()
    except ConnectionError:
        sys.exit('ERROR: No internet connection')
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
                subprocess.Popen(['notify-send', title, body])
            # add to history
            with open(HISTORY_LOCATION, 'a') as f:
                f.write('{}\n'.format(match['id']))
