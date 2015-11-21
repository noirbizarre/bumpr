#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Bump'R: Version bumper and Python package releaser

- Clean-up release artifact
- Bump version and tag it
- Build a source distrbution and upload on PyPI
- Update version for new develpoment cycle
- Can run test suite before
- Can be customized with a config file
- Extensible with hooks
'''

from .__about__ import __description__, __version__  # noqa


def main():
    import sys
    from bumpr import log
    log.init()

    from bumpr.config import Config
    from bumpr.releaser import Releaser
    from bumpr.helpers import BumprError
    from logging import DEBUG, INFO, getLogger

    config = Config.parse_args()
    getLogger().setLevel(DEBUG if config.verbose else INFO)
    try:
        releaser = Releaser(config)
        releaser.release()
    except BumprError as error:
        getLogger(__name__).error(str(error))
        sys.exit(1)
