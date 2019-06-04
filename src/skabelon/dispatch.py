"""Skabelon dispatch script for curtissand.com."""
from pathlib import Path
from time import strftime

def dispatch(**kwargs):
    now = strftime('%Y-%m-%d %H:%M')

    dist = Path('./dist')
    jobs = [
        ('index.html',
         {'title': 'home', 'date': now},
         dist.joinpath('index.html')),
        # ('projects.html',
        #  {'title': 'home', 'date': now},
        #  'projects.html'),
    ]

    for template, context, outfile in jobs:
        print('Rendering template "%s" to file "%s"' % (template, outfile))
        yield template, context, outfile
