# -*- coding: utf-8 -*-

from bumpr.version import Version


def test_default_constructor():
    version = Version()

    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 0
    assert version.suffix is None


def test_constructor():
    version = Version(1, suffix="dev")

    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0
    assert version.suffix == "dev"


def test_bump_major():
    version = Version(1, 2, 3, "dev")

    version.bump(Version.MAJOR)

    assert version.major == 2
    assert version.minor == 0
    assert version.patch == 0
    assert version.suffix is None


def test_bump_minor():
    version = Version(1, 2, 3, "dev")

    version.bump(Version.MINOR)

    assert version.major == 1
    assert version.minor == 3
    assert version.patch == 0
    assert version.suffix is None


def test_bump_patch():
    version = Version(1, 2, 3, "dev")

    version.bump(Version.PATCH)

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 4
    assert version.suffix is None


def test_bump_suffix():
    version = Version(1, 2, 3, "dev")

    version.bump(suffix="rc1")

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix == "rc1"


def test_bump_unsuffix():
    version = Version(1, 2, 3, "dev")

    version.bump(unsuffix=True)

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix is None


def test_bump_suffix_override_unsuffix():
    version = Version(1, 2, 3, "dev")

    version.bump(suffix="rc1", unsuffix=True)

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix == "rc1"


def test_bump_no_effect():
    version = Version(1, 2, 3, "dev")

    version.bump(unsuffix=False)

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix == "dev"


def test_copy():
    version = Version(1, 2, 3, "dev").copy()

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix == "dev"


def test_copy_bump():
    version = Version(1, 2, 3, "dev").copy(part=Version.MINOR, unsuffix=True)

    assert version.major == 1
    assert version.minor == 3
    assert version.patch == 0
    assert version.suffix is None


def test_parse():
    version = Version.parse("1.2.3")

    assert version is not None
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix is None


def test_parse_with_suffix():
    version = Version.parse("1.2.3.rc4")

    assert version is not None
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.suffix == "rc4"
