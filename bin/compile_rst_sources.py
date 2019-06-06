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
import json
import shutil
from pathlib import Path
from xml.etree.ElementTree import fromstring

from docutils.core import publish_parts
from docutils.core import publish_doctree


VERSION = "0.1"
VERBOSE = False
DEBUG = False

METADATA_FILE = 'metadata.json'  # File of metadata about the posts

# {filename: json contents, ...}
JSON_DATA = {METADATA_FILE: {'categories': [], 'tags': [], 'ids': [], 'posts': {}}}


class PostMetadata():
    def __init__(self, category, tags, summary, date, title,
                 html, source, **kwargs):
        self.category = category
        self.tags = tags
        self.summary = summary
        self.date = date
        self.title = title
        self.html = html
        self.source = source
        self.sanitize_tags()
        self._set_id()

    def _set_id(self):
        """Set the post's ID while ensuring uniqueness."""
        self.id = str(int(self.date.replace('-', '').replace(' ', '').replace(':', '')))
        if self.id in JSON_DATA[METADATA_FILE]['ids']:
            test_suffix = 0
            new_id = '%s%02d' % (self.id, test_suffix)
            while new_id in JSON_DATA[METADATA_FILE]['ids']:
                test_suffix += 1
                new_id = '%s%02d' % (self.id, test_suffix)
            self.id = new_id

    def __repr__(self):
        return 'PostMetadata{date: %s, title: %s}' % (self.date, self.title)

    def sanitize_tags(self):
        """Parse the tags string into a list of tags."""
        new_tags = []
        for part in self.tags.split(' '):  # some tags delimited by space
            for sub_part in part.split(','):  # some tags delimited by comma
                sub_part = sub_part.strip()
                if sub_part:  # ignore empty string
                    if sub_part not in new_tags:
                        new_tags.append(sub_part)
        self.tags = new_tags

    def json(self):
        return {
            "category": self.category,
            "tags": self.tags,
            "summary": self.summary,
            "date": self.date,
            "title": self.title,
            "html": self.html,
            "source": self.source}


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

    # sort post lists chronologically with newest first
    for key in JSON_DATA[METADATA_FILE]:
        if key in ['posts']:
            continue
        reversed = False if key in ['tags', 'categories'] else True
        JSON_DATA[METADATA_FILE][key].sort(reverse=reversed)

    # write out all JSON files
    for json_file, data in JSON_DATA.items():
        vprint('Writing JSON file %s' % json_file)
        with open(Path(sources, json_file), 'w') as fout:
            json.dump(data, fout)
    return 0


def visit_dir(src_dir, root=None):
    """Visit all files and subdirectories inside the given source dir."""
    relative_root = root if root else src_dir
    for child in src_dir.iterdir():
        if child.is_dir():
            visit_dir(child, relative_root)
        else:
            visit_file(child, relative_root)


def visit_file(src_file, root):
    """If the given file is an RST source file, compile it to HTML sources."""
    if (not src_file.exists() or
            not src_file.is_file() or
            not src_file.suffix in ['.rst', '.RST']):
        return
    fname = src_file.with_suffix('.html')

    vprint(src_file)
    info = get_docinfo(src_file)

    parts = publish_parts(src_file.read_text(), writer_name='html')

    info['title'] = parts['title']

    dprint('  writing to %s' % fname)
    with open(fname, 'w') as fout:
        fout.write('<p>%s</p>\n%s' % (info['summary'], parts['body']))
    # info['html'] = str(fname.relative_to(root))
    info['html'] = str(Path('pages', fname.relative_to(root)))

    # convert *.rst files to *.txt so browsers can server them correctly
    info['source'] = str(src_file.relative_to(root).with_suffix('.txt'))
    shutil.move(src_file, src_file.with_suffix('.txt'))
    dprint('  docinfo: %s' % info)
    gather_data(info)


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


def gather_data(docinfo):
    """Gather the docinfo data for each post."""
    global JSON_DATA
    post = PostMetadata(**docinfo)

    # don't gather json data for posts with no category
    if not post.category:
        return

    JSON_DATA[METADATA_FILE]['posts'][post.id] = post.json()
    JSON_DATA[METADATA_FILE]['ids'].append(post.id)

    for tag in post.tags:
        if tag and tag not in JSON_DATA[METADATA_FILE]['tags']:
            JSON_DATA[METADATA_FILE]['tags'].append(tag)

    if post.category:  # ignore posts with no category (i.e. about.rst)
        category = post.category + '.json'
        if post.category not in JSON_DATA[METADATA_FILE]['categories']:
            JSON_DATA[METADATA_FILE]['categories'].append(post.category)
        if post.category in JSON_DATA[METADATA_FILE]:
            JSON_DATA[METADATA_FILE][post.category].append(post.id)
        else:
            JSON_DATA[METADATA_FILE][post.category] = [post.id]


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
