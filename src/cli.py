"""
Small click-based CLI app for Benz-Finder to run helper commands
"""

import click

from utils import pullnsave


@click.group()
def cli():
    pass


@click.group(name='list')
def list_group():
    """Commands for listing data from PullNSave"""
    pass


@click.command(name='locations')
def list_locations():
    """List all PullNSave locations"""
    stores = pullnsave.get_stores()
    click.echo(stores)


@click.command(name='makes')
def list_makes():
    """List all available makes from PullNSave"""
    makes = pullnsave.get_makes()
    click.echo(makes)


@click.command(name='models')
@click.option('--make', prompt='Make', help='Make/Manufacturer to search models for')
def list_models(make: str):
    """List all available models for a make from PullNSave"""
    models = pullnsave.get_models(make)
    click.echo(models)


cli.add_command(list_group)
list_group.add_command(list_locations)
list_group.add_command(list_makes)
list_group.add_command(list_models)


if __name__ == '__main__':
    cli()
