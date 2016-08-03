import json
import os
import subprocess

from jinja2 import Template
import click

from gosuticker import Match
from gosuticker.matchticker import GosuTicker

DEFAULT_TEMPLATE = "{{opp1}} vs {{opp2}} in {{time}}"
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
        click.echo('default template: "{}"'.format(DEFAULT_TEMPLATE))
        click.echo('template keys:')
        for k in Match.keys:
            click.echo('    {}'.format(k))
        return
    if not game:
        raise click.BadParameter('Missing required parameter "game"')
    if game not in GosuTicker.games:
        click.echo('Unknown game "{}", see --list-games for available'.format(game), err=True)
        return
    ticker = GosuTicker(game)
    matches = ticker.download_matches()
    if is_json:
        click.echo(json.dumps(list(matches), indent=2, sort_keys=True))
        return
    template = template or DEFAULT_TEMPLATE
    template = Template(template)
    for m in matches:
        for k, v in m.items():
            locals()[k] = v
        click.echo(template.render(locals()))


@cli.command('notify', help='notify if a specific team plays')
@click.argument('game')
@click.argument('team')
@click.option('-s', '--seconds', default=900,
              help='seconds threshold before sending out the notification (default=900)')
@click.option('-m', '--minutes', default=0,
              help='minutes threshold before sending out the notification (default=15)')
@click.option('-p', '--pushbullet', is_flag=True,
              help='Use pushbullet notification instead system notify-send')
@click.option('-k', '--pushbullet-key', help='Pushbullet API key to use to send the notification, '
                                       'can be set through enviroment variable PUSHBULLET_API')
def notify(game, team, seconds, minutes, pushbullet, pushbullet_key):
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
    matches = GosuTicker(game).download_matches()
    for match in matches:
        if int(match['time_secs']) > int(seconds):
            continue
        if team == match['opp1'].lower() or team == match['opp2'].lower():
            # already in history?
            with open(HISTORY_LOCATION, 'r') as f:
                if match['id'] in f.read():
                    continue
            # notify
            title = "{} vs {} in {}".format(match['opp1'], match['opp2'], match['time'])
            body = match['url']
            if pushbullet:
                push = Pushbullet(pushbullet_key)
                push.push_note(title, body)
            else:
                subprocess.Popen(['notify-send', title, body])
            # add to history
            with open(HISTORY_LOCATION, 'a') as f:
                f.write('{}\n'.format(match['id']))
