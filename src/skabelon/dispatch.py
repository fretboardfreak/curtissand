"""Skabelon dispatch script for curtissand.com."""
from pathlib import Path
from time import strftime

def dispatch(**kwargs):
    now = strftime('%Y-%m-%d %H:%M')

    dist = Path('./dist')
    jobs = [
        ('index.html',
         {'title': 'Home', 'date': now, 'active_nav': 'index'},
         dist.joinpath('index.html')),
        ('projects.html',
         {'title': 'Projects', 'date': now, 'active_nav': 'projects'},
         dist.joinpath('projects.html')),
        ('posts.html',
         {'title': 'Posts', 'date': now, 'active_nav': 'posts'},
         dist.joinpath('posts.html')),
        ('about.html',
         {'title': 'About', 'date': now, 'active_nav': 'about'},
         dist.joinpath('about.html'))
    ]

    for template, context, outfile in jobs:
        print('Rendering template "%s" to file "%s"' % (template, outfile))
        yield template, context, outfile
