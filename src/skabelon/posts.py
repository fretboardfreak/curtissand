"""Skabelon dispatch script for the posts of curtissand.com."""

import os
import json
from pathlib import Path
from time import strftime

HOST = None
METADATA = None
IMAGES_DIR = None


class NoImageDirException(Exception):
    pass


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

    if 'images' not in kwargs:
        raise Exception('posts.py dispatch script requires a "images" '
                        'path as a dispatch option.')
    global IMAGES_DIR
    IMAGES_DIR = Path(kwargs['images'])

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

    file_metadata = None
    for post_data in METADATA["posts"].values():
        post_fname = Path(post_data['html']).name
        if post_data['html'].endswith(str(src_file.relative_to(root))):
            file_metadata = post_data
            break
    if not file_metadata:
        print('No metadata available for %s. Skipping file!' % str(src_file))
        return

    try:
        template_name, context = get_template_and_context(
            src_file, file_metadata, root)
    except NoImageDirException:
        print('No image dir matching gallery: %s' % str(src_file))
        return

    outfile = Path(dest, src_file.relative_to(root))
    if not outfile.parent.exists():
        os.makedirs(outfile.parent)

    print('rendering file: %s' % src_file.relative_to(root))
    return template_name, context, str(outfile)


def get_template_and_context(src_file, file_metadata, root):
    """Build a context dict for passing into the jinja2 render method."""
    context = {'title': file_metadata['title'],
               'date': file_metadata['date'],
               'active_nav': None,
               'host': HOST,
               'metadata': file_metadata}
    with open(src_file, 'r') as fin:
        context['content'] = fin.read()

    template_name = 'post.html'
    if src_file.relative_to(root).parts[0] == "galleries":
        template_name = 'gallery.html'
        context['images'] = get_gallery_images(src_file)


    return template_name, context


def get_gallery_images(src_file):
    """Create a list of images for the given gallery file."""
    img_thumb_pairs = []
    # find an image dir that matches the name of this gallery file
    for child in IMAGES_DIR.iterdir():
        if child.name == src_file.stem:
            break  # exit this loop leaving child set to the matched dir
    else:
        raise NoImageDirException('no image dir matching this gallery.')

    # walk through all files inside the image dir
    for img_root, dirnames, fnames in os.walk(child):
        if len(fnames) == 0:
            print(' no images, skipping gallery')
            return
        thumb_dir = None
        if 'thumbs' in dirnames:
            dirnames.pop(dirnames.index('thumbs'))
            thumb_dir = Path(img_root, 'thumbs')
        # List all images with their corresponding thumbnail if one exists
        for image_file in fnames:
            if image_file.startswith('.'):  # skip files like ".DS_Store"
                continue
            big_img = Path(img_root, image_file)
            big_img_relative = str(big_img.relative_to(IMAGES_DIR))
            if thumb_dir:
                for match in thumb_dir.glob(big_img.stem + '*'):
                    if match.stem == big_img.stem:
                        img_thumb_pairs.append(
                            (big_img_relative,
                             str(match.relative_to(IMAGES_DIR))))
            else:
                img_thumb_pairs.append((big_img_relative, None))

    return sorted(img_thumb_pairs, key=lambda i: i[0])
