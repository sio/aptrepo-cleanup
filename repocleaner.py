#!/usr/bin/env python3
'''
Update APT package lists, disable all repos that cause errors
(invalid GPG signature, HTTP errors, etc)

Print machine-readable JSON on standard output for further processing

Print human-readable error messages that were encountered during 'apt update'
attempts to stderr
'''

import json
import re
import sys
from pathlib import Path

import apt.cache
import aptsources.sourceslist


URL_REGEX = re.compile(r'''(?:https?|ftp)://\S+''')

RC_SUCCESS = 0
RC_CHANGED = 200
RC_ERROR = 2


def update_cache():
    cache = apt.Cache()
    cache.update()
    cache.commit()


def get_failed_repos(exception):
    errors = [e.strip() for e in str(exception).split(',')]
    for error in errors:
        if error.startswith('W:'):
            continue
        for url in URL_REGEX.findall(error):
            yield url.rstrip("'")


def disable_repos(urls):
    sources = aptsources.sourceslist.SourcesList()
    disabled = []
    urls_seen = 0
    for url in urls:
        if not url:
            continue
        urls_seen += 1
        for source in sources:  # deb822 is not supported yet
            if not source.uri or source.disabled:
                continue
            if source.uri.startswith(url) or url.startswith(source.uri):
                disabled.append(str(source))
                source.set_enabled(False)
                break
        else:  # look at deb822 sources manually
            disabled.extend(disable_deb822(url))
    if disabled:
        sources.save()
    elif urls_seen:
        sys.stderr.write(f'No repos were disabled even though {urls_seen} URLs were provided\n')
        sys.exit(RC_ERROR)
    else:
        sys.stderr.write(f'Could not disable repos: empty URL sequence was provided\n')
        sys.exit(RC_ERROR)
    return disabled


def disable_deb822(url):
    disabled = []
    for source in Path('/etc/apt/sources.list.d').glob('*.sources'):
        with source.open('r') as s:
            for line in s:
                if not line.strip().startswith('URIs'):
                    continue
                for match in URL_REGEX.findall(line):
                    if match.startswith(url) or url.startswith(match):
                        disabled.append(str(source))
                        source.rename(source.with_suffix('.deb822-disabled'))
    return disabled


def main():
    disabled_repos = []
    while True:
        try:
            update_cache()
        except apt.cache.FetchFailedException as exc:
            sys.stderr.write(f'{exc}\n')
            urls = get_failed_repos(exc)
            disabled_repos.extend(disable_repos(urls))
            continue
        except KeyboardInterrupt:
            sys.exit(RC_ERROR)
        break
    report = dict(
        disabled=disabled_repos,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if disabled_repos:
        sys.exit(RC_CHANGED)
    else:
        sys.exit(RC_SUCCESS)


if __name__ == '__main__':
    main()
