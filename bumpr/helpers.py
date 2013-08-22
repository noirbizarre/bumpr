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


def execute(command, verbose=False, replacements={}, dryrun=False):
    if not command:
        return
    for cmd in command.split('\n'):
        if cmd.strip():
            cmd = cmd.format(**replacements).strip()
            if dryrun:
                logger.info('dry run execute: {0}'.format(cmd))
            elif verbose:
                subprocess.check_call(shlex.split(cmd))
            else:
                try:
                    check_output(shlex.split(cmd))
                except subprocess.CalledProcessError as exception:
                    logger.error('Command "%s" failed with exit code %s', cmd, exception.returncode)
                    print(exception.output)
