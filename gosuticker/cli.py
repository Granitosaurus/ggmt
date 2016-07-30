from jinja2 import Template
import click

from gosuticker import Match
from gosuticker.matchticker import GosuTicker

DEFAULT_TEMPLATE = "{{opp1}} vs {{opp2}} in {{time}}"


@click.command()
@click.version_option()
@click.argument('game', required=False)
@click.option('-t', '--template', help='set template')
@click.option('--list-games', help='list supported games', is_flag=True)
@click.option('--help-template', help='print help message for how to format template', is_flag=True)
def cli(game, list_games, template, help_template):
    if help_template:
        click.echo('Gosuticker is using Jinja2 templating engine')
        click.echo('default template: "{}"'.format(DEFAULT_TEMPLATE))
        click.echo('template keys:')
        for k in Match.keys:
            click.echo('    {}'.format(k))
        return
    if list_games:
        for game in GosuTicker.games:
            click.echo(game)
        return
    if not game:
        raise click.BadParameter('Missing required parameter "game"')
    if game not in GosuTicker.games:
        click.echo('Unknown game "{}", see --list-games for available'.format(game), err=True)
        return
    template = template or DEFAULT_TEMPLATE
    template = Template(template)
    ticker = GosuTicker(game)
    matches = ticker.download_matches()
    for m in matches:
        for k, v in m.items():
            locals()[k] = v
        click.echo(template.render(locals()))
