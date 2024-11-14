import logging
import re
from datetime import datetime
from difflib import unified_diff
from typing import Optional

from .forge import FORGES
from .helpers import BumprError, execute
from .hooks import HOOKS
from .vcs import VCS
from .version import Version

logger = logging.getLogger(__name__)


class Releaser:
    """
    Release workflow executor
    """

    def __init__(self, config):
        self.config = config

        with open(config.file) as f:
            match = re.search(config.regex, f.read())
            try:
                version_string = match.group("version")
                self.prev_version = Version.parse(version_string)
            except Exception:
                raise BumprError(f"Unable to extract version from {config.file}")

        logger.debug("Previous version: {0}".format(self.prev_version))

        self.version = self.prev_version.copy()
        self.version.bump(config.bump.part, config.bump.unsuffix, config.bump.suffix)
        logger.debug("Bumped version: {0}".format(self.version))

        self.next_version = self.version.copy()
        self.next_version.bump(config.prepare.part, config.prepare.unsuffix, config.prepare.suffix)
        logger.debug("Prepared version: {0}".format(self.next_version))

        self.tag_label = self.config.tag_format.format(version=self.version)
        logger.debug("Tag: {0}".format(self.tag_label))
        if self.config.tag_annotation:
            self.tag_annotation = self.config.tag_annotation.format(version=self.version)
            logger.debug("Tag annotation: {0}".format(self.tag_annotation))

        self.timestamp = None

        if config.vcs:
            self.vcs = VCS[config.vcs](verbose=config.verbose)
            self.vcs.validate(dryrun=config.dryrun)

        if config.forge:
            self.forge = FORGES[config.forge](verbose=config.verbose)

        if config.dryrun:
            self.modified = {}
            self.diffs = {}

        self.hooks = [hook(self) for hook in HOOKS if self.config[hook.key]]

    def execute(self, command, version=None, verbose=None):
        version = version or self.version
        verbose = verbose or self.config.verbose
        replacements = dict(version=version, date=self.timestamp, **version.__dict__)
        execute(
            command,
            replacements=replacements,
            dryrun=self.config.dryrun,
            verbose=verbose,
        )

    def release(self):
        self.timestamp = datetime.now()

        if self.config.bump_only:
            self.bump()
        elif self.config.prepare_only:
            self.prepare()
        else:
            self.clean()
            self.test()
            self.bump()
            self.publish()
            self.prepare()
            self.push()

    def test(self):
        if self.config.tests:
            if self.config.skip_tests:
                logger.info("Skip test suite")
                return
            logger.info("Running test suite")
            self.execute(self.config.tests, verbose=True)

    def bump(self):
        logger.info(f"Bump version {self.version}")

        replacements = [(str(self.prev_version), str(self.version))]

        for hook in self.hooks:
            hook.bump(replacements)

        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(
                self.config.bump.message.format(
                    version=self.version,
                    tag=self.tag_label,
                    date=self.timestamp,
                    **self.version.__dict__,
                )
            )
            self.tag()

        if self.config.dryrun:
            self.display_diff()
            self.diffs.clear()

    def prepare(self):
        if self.version == self.next_version:
            logger.info("Skip prepare phase")
            return
        logger.info(f"Prepare version {self.next_version}")

        replacements = [(str(self.version), str(self.next_version))]

        for hook in self.hooks:
            hook.prepare(replacements)

        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(
                self.config.prepare.message.format(
                    version=self.next_version,
                    tag=self.tag_label,
                    date=self.timestamp,
                    **self.next_version.__dict__,
                )
            )

        if self.config.dryrun:
            self.display_diff()

    def clean(self):
        """Clean the workspace"""
        if self.config.clean:
            logger.info("Cleaning")
            self.execute(self.config.clean)

    def perform(self, filename, before, after):
        if before == after:
            return
        if self.config.dryrun:
            self.modified[filename] = after
            diff = unified_diff(before.split("\n"), after.split("\n"), lineterm="")
            self.diffs[filename] = diff
        else:
            with open(filename, "w", encoding=self.config.encoding) as f:
                f.write(after)

    def bump_files(self, replacements):
        for filename in [self.config.file] + self.config.files:
            if self.config.dryrun and filename in self.modified:
                before = self.modified[filename]
            else:
                with open(filename, "r", encoding=self.config.encoding) as current_file:
                    before = current_file.read()
            after = before
            for token, replacement in replacements:
                after = after.replace(token, replacement)
            self.perform(filename, before, after)

    def publish(self):
        """Publish the current release to PyPI and to the Forge if defined"""
        if self.config.publish:
            logger.info("Publish")
            self.execute(self.config.publish)

            if self.config.forge:
                self.create_forge_release()

    def tag(self):
        if self.config.commit and self.config.tag:
            if self.config.tag_annotation:
                logger.debug(f"Tag: {self.tag_label} Annotation: {self.tag_annotation}")
                if not self.config.dryrun:
                    self.vcs.tag(self.tag_label, self.tag_annotation)
                else:
                    logger.dryrun(f"tag: {self.tag_label} annotation: {self.tag_annotation}")
            else:
                logger.debug(f"Tag: {self.tag_label}")
                if not self.config.dryrun:
                    self.vcs.tag(self.tag_label)
                else:
                    logger.dryrun(f"tag: {self.tag_label}")

    def create_forge_release(self, notes: Optional[str] = None):
        if self.config.tag:
            logger.debug(f"Forge release: {self.tag_label} Forge release notes: {notes}")
            if not self.config.dryrun:
                self.forge.release(version=self.tag_label, notes=notes)
            else:
                logger.dryrun(f"Forge release: {self.tag_label} Forge release notes: {notes}")  # type: ignore

    def commit(self, message):
        if self.config.commit:
            logger.debug(f"Commit: {message}")
            if not self.config.dryrun:
                self.vcs.commit(message)
            else:
                logger.dryrun(f"commit: {message}")

    def push(self):
        if self.config.vcs and self.config.commit and self.config.push:
            logger.info("Push to upstream repository")
            if not self.config.dryrun:
                self.vcs.push()
            else:
                logger.dryrun("push to remote repository")

    def display_diff(self):
        for filename, diff in self.diffs.items():
            logger.diff(filename)
            for line in diff:
                logger.diff(line)
            logger.diff("")
