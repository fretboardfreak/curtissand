"""Skabelon dispatch script for the static pages of curtissand.com."""
from pathlib import Path
from time import strftime

def dispatch(**kwargs):
    if 'host' not in kwargs:
        raise Exception('posts.py dispatch script requires a "host" '
                        'dispatch option.')
    host = kwargs['host']
    now = strftime('%Y-%m-%d %H:%M')

    dist = Path('./dist')
    jobs = [
        ('index.html',
         {'title': 'Home', 'date': now, 'active_nav': 'index', 'host': host},
         dist.joinpath('index.html')),
        ('projects.html',
         {'title': 'Projects', 'date': now, 'active_nav': 'projects',
          'host': host},
         dist.joinpath('projects.html')),
        ('posts.html',
         {'title': 'Posts', 'date': now, 'active_nav': 'posts', 'host': host},
         dist.joinpath('posts.html')),
        ('about.html',
         {'title': 'About', 'date': now, 'active_nav': 'about', 'host': host},
         dist.joinpath('about.html'))
    ]

    for template, context, outfile in jobs:
        print('Rendering template "%s" to file "%s"' % (template, outfile))
        yield template, context, outfile
