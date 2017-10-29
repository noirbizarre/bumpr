# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

import click

from bumpr import __version__
from bumpr.config import Config, ValidationError
from bumpr.helpers import BumprError
from bumpr.log import init_logging
from bumpr.releaser import Releaser
from bumpr.vcs import VCS
from bumpr.version import Version


log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {
    'auto_envvar_prefix': 'bumpr',
    'help_option_names': ['-?', '-h', '--help'],
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--version', is_flag=True, help='Print the current version')
@click.option('-c', '--config', default='bumpr.rc', help='Specify a configuration file')
@click.option('-d', '--dryrun', is_flag=True, help='Do not write anything and display a diff')
@click.option('-st', '--skip-tests', is_flag=True, help='Skip tests')
# Bump
@click.option('-M', '--major', 'part', flag_value=Version.MAJOR, help="Bump major version")
@click.option('-m', '--minor', 'part', flag_value=Version.MINOR, help="Bump minor version")
@click.option('-p', '--patch', 'part', flag_value=Version.PATCH, help="Bump patch version")
@click.option('-s', '--suffix', help="Set suffix")
@click.option('-u', '--unsuffix', is_flag=True, default=None, help="Unset suffix")
# Version control system
@click.option('--vcs', type=click.Choice(VCS.keys()), default=None, help='VCS implementation')
@click.option('-C/-nc', '--commit/--no-commit', is_flag=True, default=None, help='Commit or not')
@click.option('-P/-np', '--push/--no-push', is_flag=True, default=None, help='Push changes to remote repository')
@click.pass_context
def cli(ctx, verbose, **kwargs):
    '''Version bumper and Python package releaser'''
    init_logging(verbose)
    if ctx.params.get('version'):
        click.echo(__version__)
        ctx.exit()

    try:
        config = Config(parsed_args=ctx.params)
    except Exception as e:
        msg = 'Invalid configuration: {0}'.format(e)
        log.error(msg)
        ctx.exit(1)

    try:
        config.validate()
    except ValidationError as e:
        msg = 'Invalid configuration: {0}'.format(e)
        log.error(msg)
        ctx.exit(1)

    try:
        releaser = Releaser(config)
        releaser.release()
    except BumprError as error:
        log.error(str(error))
        ctx.exit(1)
