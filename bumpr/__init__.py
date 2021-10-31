"""
Bump'R: Version bumper and Python package releaser

- Clean-up release artifact
- Bump version and tag it
- Build a source distrbution and upload on PyPI
- Update version for new develpoment cycle
- Can run test suite before
- Can be customized with a config file
- Extensible with hooks
"""

from .__about__ import __description__, __version__  # noqa
