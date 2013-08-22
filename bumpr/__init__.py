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

__version__ = '0.1.0'
__description__ = 'Version bumper and Python package releaser'


def main():
    from bumpr import log
    from bumpr.config import Config
    from bumpr.releaser import Releaser
    from logging import DEBUG, INFO

    config = Config.parse_args()
    log.init(DEBUG if config.verbose else INFO)
    releaser = Releaser(config)
    releaser.release()
