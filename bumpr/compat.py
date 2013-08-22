# -*- coding: utf-8 -*-
import subprocess


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
