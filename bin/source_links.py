#!/usr/bin/env python3
"""Create or Remove links to the static source files."""

import os
import sys
import argparse
import subprocess
from pathlib import Path


VERSION = "0.1"
VERBOSE = False
DEBUG = False

# {'hostname': [(src, dest), ...], ...}
LINKS_BY_HOST = {
    'hackmanite': [
        (Path('/Users/csand/Pictures/website/cs'), Path('images')),
        (Path('/Users/csand/git/fret/blog'), Path('sources/blog')),
        (Path('/Users/csand/git/fret/ref'), Path('sources/ref')),
        (Path('/Users/csand/git/fret/galleries'), Path('sources/galleries')),
        (Path('/Users/csand/git/fret/about.rst'), Path('sources/about.rst')),
        (Path('/Users/csand/git/fret/projects.rst'), Path('sources/projects.rst')),
    ],
    'obsidian': [
        (Path('/home/csand/storage/pics/website/cs'), Path('images')),
        (Path('/home/csand/git/fret/blog'), Path('sources/blog')),
        (Path('/home/csand/git/fret/ref'), Path('sources/ref')),
        (Path('/home/csand/git/fret/galleries'), Path('sources/galleries')),
        (Path('/home/csand/git/fret/about.rst'), Path('sources/about.rst')),
        (Path('/home/csand/git/fret/projects.rst'), Path('sources/projects.rst')),
    ]
}
EXTRA_PATHS_TO_REMOVE = [Path('sources')]


def hostname():
    """Get hostname and cache for later."""
    if 'value' not in hostname.__dict__:
        hostname.__dict__['value'] = (
            subprocess.check_output('hostname').decode().strip())
    return hostname.__dict__['value']


def rmpath(path):
    """Call the correct remove method for the given path."""
    if path.is_symlink():
        os.remove(path)
    elif path.is_dir():
        os.rmdir(path)


def remove():
    """Remove the symlinks to the static source files."""
    for src, dest in LINKS_BY_HOST[hostname()]:
        if dest.exists():
            vprint('removing %s' % dest)
            rmpath(dest)
    for other_path in EXTRA_PATHS_TO_REMOVE:
        vprint('removing %s' % other_path)
        rmpath(other_path)


def create():
    """Create the symlinks to the static source files."""
    for src, dest in LINKS_BY_HOST[hostname()]:
        if dest.exists():
            continue
        if not dest.parent.exists():
            vprint('making dir: %s' % dest.parent)
            os.makedirs(dest.parent, exist_ok=True)
        vprint('linking: %s -> %s' % (src, dest))
        os.symlink(src, dest)


def main():
    args = parse_cmd_line()
    if args.remove:
        remove()
    else:
        create()
    return 0


def parse_cmd_line():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--version', help='Print the version and exit.', action='version',
        version='%(prog)s {}'.format(VERSION))
    DebugAction.add_parser_argument(parser)
    VerboseAction.add_parser_argument(parser)
    parser.add_argument(
        '-r', '--remove', help='Remove links to source files.',
        action='store_true', default=False)
    return parser.parse_args()


def dprint(msg):
    """Conditionally print a debug message."""
    if DEBUG:
        print(msg)


def vprint(msg):
    """Conditionally print a verbose message."""
    if VERBOSE:
        print(msg)


class DebugAction(argparse.Action):
    """Enable the debugging output mechanism."""

    sflag = '-d'
    flag = '--debug'
    help = 'Enable debugging output.'

    @classmethod
    def add_parser_argument(cls, parser):
        parser.add_argument(cls.sflag, cls.flag, help=cls.help, action=cls)

    def __init__(self, option_strings, dest, **kwargs):
        super(DebugAction, self).__init__(option_strings, dest, nargs=0,
                                          default=False, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        global DEBUG
        DEBUG = True
        setattr(namespace, self.dest, True)


class VerboseAction(DebugAction):
    """Enable the verbose output mechanism."""

    sflag = '-v'
    flag = '--verbose'
    help = 'Enable verbose output.'

    def __call__(self, parser, namespace, values, option_string=None):
        global VERBOSE
        VERBOSE = True
        setattr(namespace, self.dest, True)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        sys.exit(0)
    except KeyboardInterrupt:
        print('...interrupted by user, exiting.')
        sys.exit(1)
    except Exception as exc:
        if DEBUG:
            raise
        else:
            print('Unhandled Error:\n{}'.format(exc))
            sys.exit(1)
