from functools import cmp_to_key

import semver


def version_comparator():
    def compare(a, b):
        a_version = a.version.lower()
        b_version = b.version.lower()

        if a_version == "unreleased":
            return -1
        elif b_version == "unreleased":
            return 1
        else:
            return semver.VersionInfo.parse(a_version).compare(b_version) * -1

    return cmp_to_key(compare)


def change_comparator():
    def compare(a, b):
        a_version = a.change_type.lower()
        b_version = b.change_type.lower()

        if a_version < b_version:
            return -1
        elif a_version > b_version:
            return 1
        else:
            return 0

    return cmp_to_key(compare)
