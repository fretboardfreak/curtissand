#!/usr/bin/env python3
"""Compile RST Sources: a script written for Curtis Sand's website project.

Given a directory of RST files, iterate through and compile the RST files into
different HTML files. More than one HTML file is generated given a single
source file. The resulting HTML files can be used to display the title,
document info, summary and article sections of the source RST document.
"""

import argparse
import os
import sys
from pathlib import Path
from xml.etree.ElementTree import fromstring

from docutils.core import publish_parts
from docutils.core import publish_doctree


VERSION = "0.1"
VERBOSE = False
DEBUG = False


def main():
    """Main script logic."""
    args = parse_cmd_line()
    dprint(args)
    sources = Path(args.sources)
    if not sources.exists() or not sources.is_dir():
        print('The given SOURCE_DIR path does not appear to be a '
              'valid directory.')
        return 1
    visit_dir(sources)
    return 0


def visit_dir(src_dir):
    """Visit all files and subdirectories inside the given source dir."""
    for child in src_dir.iterdir():
        if child.is_dir():
            visit_dir(child)
        else:
            visit_file(child)


def visit_file(src_file):
    """If the given file is an RST source file, compile it to HTML sources."""
    if (not src_file.exists() or
            not src_file.is_file() or
            not src_file.suffix in ['.rst', '.RST']):
        return
    fname = src_file.name[:-len(src_file.suffix)]  # remove suffix
    title = os.path.join(*src_file.parts[:-1], fname + '_title.html')
    body = os.path.join(*src_file.parts[:-1], fname + '_body.html')

    vprint(src_file)
    info = get_docinfo(src_file)
    dprint('  docinfo: %s' % info)
    parts = publish_parts(src_file.read_text(), writer_name='html')

    dprint('  writing section title to %s' % title)
    with open(title, 'w') as fout:
        fout.write(parts['title'])

    dprint('  writing section body to %s' % body)
    with open(body, 'w') as fout:
        fout.write('<p>%s</p>\n%s' % (info['summary'], parts['body']))


def get_docinfo(src_file):
    """Using the Docutils doctree object, gather the document info fields."""
    info = {}
    date_str = 'date'
    doctree = fromstring(publish_doctree(src_file.read_text()).asdom().toxml())
    for field in doctree.iter(tag='field'):
        name = next(field.iter(tag='field_name'))
        value = next(field.iter(tag='field_body'))
        info[name.text] = ''.join(value.itertext())
    info[date_str] = doctree.find('docinfo').find('date').text
    return info


def parse_cmd_line():
    """Generate an ArgumentParser for the script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--version', help='Print the version and exit.', action='version',
        version='%(prog)s {}'.format(VERSION))
    DebugAction.add_parser_argument(parser)
    VerboseAction.add_parser_argument(parser)
    parser.add_argument(
        help="The directory of RST sources to work on.", metavar="SOURCE_DIR",
        dest='sources')
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
