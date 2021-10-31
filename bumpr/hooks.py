from __future__ import annotations

import logging
from os.path import exists
from typing import TYPE_CHECKING

from .helpers import BumprError, execute

if TYPE_CHECKING:
    from typing import Optional

logger = logging.getLogger(__name__)

__all_ = (
    "Hook",
    "ReadTheDocHook",
    "ChangelogHook",
    "CommandHook",
    "ReplaceHook",
    "HOOKS",
)


class Hook:
    key: str = ""
    defaults: dict[str, Optional[str]] = {}

    def __init__(self, releaser):
        self.releaser = releaser
        self.verbose = releaser.config.verbose
        self.dryrun = releaser.config.dryrun
        self.config = releaser.config[self.key]
        self.validate()

    def validate(self):
        """Override this method to implement initial validation"""

    def bump(self, replacements):
        pass

    def prepare(self, replacements):
        pass


class ReadTheDocHook(Hook):
    """
    This hook set the readthedoc url corresponding to the version
    """

    key = "readthedoc"
    defaults = {
        "id": None,
        "url": "https://{id}.readthedocs.io/en/{tag}",
        "badge": "https://readthedocs.org/projects/{id}/badge/?version={tag}",
        "bump": "{version}",
        "prepare": "latest",
    }

    def url(self, tag):
        return self.config.url.format(id=self.config.id, tag=tag)

    def badge(self, tag):
        return self.config.badge.format(id=self.config.id, tag=tag)

    def bump(self, replacements):
        replacements.insert(0, (self.badge("latest"), self.badge(self.releaser.tag_label)))
        replacements.insert(0, (self.url("latest"), self.url(self.releaser.tag_label)))

    def prepare(self, replacements):
        replacements.insert(0, (self.badge(self.releaser.tag_label), self.badge("latest")))
        replacements.insert(0, (self.url(self.releaser.tag_label), self.url("latest")))


class ChangelogHook(Hook):
    """
    This hook bump the changelog version header and prepare a new section for the next release.
    """

    key = "changelog"
    defaults = {
        "file": None,
        "separator": "-",
        "bump": "{version} ({date:%Y-%m-%d})",
        "prepare": "Current",
        "empty": "Nothing yet",
    }

    def validate(self):
        if not self.config.get("file"):
            raise BumprError("Changelog file has not been specified")
        elif not exists(self.config.file):
            raise BumprError("Changelog file does not exists")

    def bump(self, replacements):
        with open(self.config.file, "r", encoding=self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.dev_header(), self.bumped_header())
        self.releaser.perform(self.config.file, before, after)

    def prepare(self, replacements):
        next_header = "\n".join(
            (
                self.dev_header(),
                "",
                "- {0}".format(self.config.empty),
                "",
                self.bumped_header(),
            )
        )
        with open(self.config.file, "r", encoding=self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.bumped_header(), next_header)
        self.releaser.perform(self.config.file, before, after)

    def dev_header(self):
        return self.underline(self.config.prepare)

    def bumped_header(self):
        title = self.config.bump.format(
            version=self.releaser.version,
            date=self.releaser.timestamp,
            **self.releaser.version.__dict__,
        )
        return self.underline(title)

    def underline(self, text):
        if self.config.separator:
            return "\n".join((text, len(text) * self.config.separator))
        else:
            return text


class CommandsHook(Hook):
    """
    This hook execute commands
    """

    key = "commands"
    defaults = {
        "bump": None,
        "prepare": None,
    }

    def bump(self, replacements):
        if self.config.bump:
            replacements = dict(
                version=self.releaser.version,
                tag=self.releaser.tag_label,
                date=self.releaser.timestamp,
                **self.releaser.version.__dict__,
            )
            execute(
                self.config.bump,
                replacements=replacements,
                verbose=self.verbose,
                dryrun=self.dryrun,
            )

    def prepare(self, replacements):
        if self.config.prepare:
            replacements = dict(
                version=self.releaser.next_version,
                tag=self.releaser.tag_label,
                date=self.releaser.timestamp,
                **self.releaser.next_version.__dict__,
            )
            execute(
                self.config.prepare,
                replacements=replacements,
                verbose=self.verbose,
                dryrun=self.dryrun,
            )


class ReplaceHook(Hook):
    """
    This hook perform replacements in files
    """

    key = "replace"
    defaults: dict[str, Optional[str]] = {}

    def bump(self, replacements):
        replacements.insert(
            0,
            (
                self.config.dev.format(
                    version=self.releaser.prev_version,
                    tag=self.releaser.tag_label,
                    date=self.releaser.timestamp,
                    **self.releaser.prev_version.__dict__,
                ),
                self.config.stable.format(
                    version=self.releaser.version,
                    tag=self.releaser.tag_label,
                    date=self.releaser.timestamp,
                    **self.releaser.version.__dict__,
                ),
            ),
        )

    def prepare(self, replacements):
        replacements.insert(
            0,
            (
                self.config.stable.format(
                    version=self.releaser.version,
                    tag=self.releaser.tag_label,
                    date=self.releaser.timestamp,
                    **self.releaser.version.__dict__,
                ),
                self.config.dev.format(
                    version=self.releaser.next_version,
                    tag=self.releaser.tag_label,
                    date=self.releaser.timestamp,
                    **self.releaser.next_version.__dict__,
                ),
            ),
        )


HOOKS = (ReadTheDocHook, ChangelogHook, CommandsHook, ReplaceHook)
