# -*- coding: utf-8 -*-
import logging
import shlex
import subprocess

logger = logging.getLogger(__name__)


def check_output(*args, **kwargs):
    '''Compatibility wrapper for Python 2.6 missin g subprocess.check_output'''
    if hasattr(subprocess, 'check_output'):
        return subprocess.check_output(*args, **kwargs)
    else:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            error = subprocess.CalledProcessError(retcode, args[0])
            error.output = output
            raise error
        return output


def execute(command, verbose=False, replacements=None, dryrun=False):
    replacements = replacements or {}
    if not command:
        return
    elif isinstance(command, (list, tuple)):
        if not isinstance(command[0], (list, tuple)):
            command = [command]
        commands = []
        for cmd in command:
            commands.append([part.format(**replacements) for part in cmd])
    else:
        commands = [shlex.split(cmd.format(**replacements)) for cmd in command.split('\n') if cmd.strip()]

    for cmd in commands:
        if dryrun:
            logger.info('dry run execute: {0}'.format(' '.join(cmd)))
        elif verbose:
            subprocess.check_call(cmd)
        else:
            try:
                check_output(cmd)
            except subprocess.CalledProcessError as exception:
                logger.error('Command "%s" failed with exit code %s', cmd, exception.returncode)
                print(exception.output)
