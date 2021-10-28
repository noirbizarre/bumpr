from __future__ import annotations

import logging
import shlex
import subprocess


class BumprError(Exception):
    pass


def check_output(*args, **kwargs):
    """A wrapper for preconfigured calls to subprocess.check_output"""
    return subprocess.check_output(
        stderr=subprocess.STDOUT, universal_newlines=True, *args, **kwargs
    )


def execute(command, verbose=False, replacements=None, dryrun=False):
    logger = logging.getLogger(__name__)
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
        command = command.format(**replacements)
        commands = [shlex.split(cmd.strip()) for cmd in command.splitlines() if cmd.strip()]

    output = ""
    for cmd in commands:
        try:
            if dryrun:
                logger.dryrun("execute: {0}".format(" ".join(cmd)))
            elif verbose:
                subprocess.check_call(cmd)
            else:
                output += check_output(cmd)
        except subprocess.CalledProcessError as exception:
            if hasattr(exception, "output") and exception.output:
                print(exception.output)
            cmd = " ".join(cmd) if isinstance(cmd, (list, tuple)) else cmd
            raise BumprError(
                'Command "{0}" failed with exit code {1}'.format(cmd, exception.returncode)
            )
    return output


class ObjectDict(dict):
    """A dictionnary with object-like attribute access and depp merge"""

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ObjectDict):
            value = ObjectDict(value)
        self[key] = value

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ObjectDict):
            value = ObjectDict(value)
        super(ObjectDict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            if isinstance(value, dict) and not isinstance(value, ObjectDict):
                value = ObjectDict(value)
            self[key] = value

    def merge(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            if isinstance(value, dict):
                if not isinstance(value, ObjectDict):
                    value = ObjectDict(value)
                if key in self and isinstance(self[key], ObjectDict):
                    self[key].merge(value)
                    continue
            self[key] = value
