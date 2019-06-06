"""Skabelon dispatch script for the posts of curtissand.com."""

import os
import json
from pathlib import Path
from time import strftime

HOST = None
METADATA = None


def dispatch(**kwargs):
    if 'host' not in kwargs:
        raise Exception('posts.py dispatch script requires a "host" '
                        'dispatch option.')
    global HOST
    HOST = kwargs['host']

    if 'sources' not in kwargs:
        raise Exception('posts.py dispatch script requires a "sources" '
                        'dispatch option.')
    sources = Path(kwargs['sources'])

    if 'dest' not in kwargs:
        raise Exception('posts.py dispatch script requires a "dest" '
                        'dispatch option.')
    dest = Path(kwargs['dest'])

    if 'metadata' not in kwargs:
        raise Exception('posts.py dispatch script requires a "metadata" '
                        'JSON file as a dispatch option.')
    metadata = kwargs['metadata']
    global METADATA
    with open(metadata, 'r') as fin:
        METADATA = json.load(fin)

    yield from visit_dir(sources, root=sources, dest=dest)


def visit_dir(src_dir, root=None, dest=None):
    """Visit all files and subdirectories inside the given source dir."""
    relative_root = root if root else src_dir
    for child in src_dir.iterdir():
        if child.is_dir():
            yield from visit_dir(child, relative_root, dest=dest)
        else:
            ret_val = visit_file(child, relative_root, dest=dest)
            if ret_val:
                yield ret_val


def visit_file(src_file, root, dest):
    """If the given file is an RST source file, compile it to HTML sources."""
    if (not src_file.exists() or
            not src_file.is_file() or
            not src_file.suffix in ['.html']):
        return

    print('rendering file: %s' % src_file.relative_to(root))
    file_metadata = None
    for post_data in METADATA["posts"].values():
        post_fname = Path(post_data['html']).name
        if post_data['html'].endswith(str(src_file.relative_to(root))):
            file_metadata = post_data
            break
    if not file_metadata:
        print('No metadata available for %s. Skipping file!' % str(src_file))
        return

    template_name = 'post.html'
    context = {'title': file_metadata['title'],
               'date': file_metadata['date'],
               'active_nav': None,
               'host': HOST,
               'metadata': file_metadata}
    with open(src_file, 'r') as fin:
        context['content'] = fin.read()

    outfile = Path(dest, src_file.relative_to(root))
    if not outfile.parent.exists():
        os.makedirs(outfile.parent)
    return template_name, context, str(outfile)
