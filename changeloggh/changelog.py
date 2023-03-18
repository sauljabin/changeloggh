import json

from jinja2 import Environment

from changeloggh.url_utils import url_join

LINK_KEY = "link"

VERSION_KEY = "version"

REPOSITORY_KEY = "repository"

VERSIONS_KEY = "versions"

JINJA_TEMPLATE = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
{% for version in versions %}
## [{{version.version.capitalize()}}]{% if version.date %} - {{version.date}}{% endif %}
{% for change in version.changes %}
### {{change.type.capitalize()}}
{% for item in change.list %}
- {{item}}
{% endfor %}{% endfor %}{% endfor %}
{% for link in links %}[{{link.version.capitalize()}}]: {{link.link}}
{% endfor %}
"""


def parser():
    pass


def load():
    pass


class Changelog:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError("Argument must be dictionary.")

        self.data = data

        if self.data.get(VERSIONS_KEY) is None:
            self.data[VERSIONS_KEY] = []

        if self.data.get(REPOSITORY_KEY) is None:
            self.data[REPOSITORY_KEY] = ""

    def __str__(self):
        return self.to_string()

    def to_string(self):
        links = []
        versions = self.data[VERSIONS_KEY]
        repository = self.data[REPOSITORY_KEY]

        if len(versions) > 1 and repository:
            for index, version in enumerate(versions[:-1]):
                previous_tag = f"v{versions[index + 1][VERSION_KEY]}"
                current_tag = f"v{version[VERSION_KEY]}"

                if index == 0:
                    current_tag = "HEAD"

                links.append(
                    {
                        VERSION_KEY: version[VERSION_KEY],
                        LINK_KEY: url_join(
                            [repository, f"/compare/{previous_tag}...{current_tag}"]
                        ),
                    }
                )

            version = versions[-1][VERSION_KEY]
            links.append(
                {
                    VERSION_KEY: version,
                    LINK_KEY: url_join([repository, f"/releases/tag/v{version}"]),
                }
            )

        env = Environment()
        template = env.from_string(JINJA_TEMPLATE)
        return template.render(versions=versions, links=links).strip()

    def to_dict(self):
        return self.data

    def to_json(self, indent=None):
        return json.dumps(self.data, indent=indent)


if __name__ == "__main__":
    cl = Changelog({})
    print(cl.to_string())
    print(cl.to_dict())
    print(cl.to_json(indent=True))
