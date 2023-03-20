from functools import cmp_to_key

import semver


def version_comparator():
    def compare(a, b):
        a_version = a["version"].lower()
        b_version = b["version"].lower()

        if a_version == "unreleased":
            return -1
        elif b_version == "unreleased":
            return 1
        else:
            return semver.VersionInfo.parse(a_version).compare(b_version) * -1

    return cmp_to_key(compare)
