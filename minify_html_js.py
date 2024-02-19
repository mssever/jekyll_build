#!/usr/bin/env python3
'''
Script to minify the HTML and JavaScript files in a given directory tree.
Only JavaScript files with the `.js` extension will be touched.
'''

import argparse
import os
from os.path import join
import urllib, urllib.request, urllib.parse # for web-based JS minifier
import http # for exception handling
import sys
import time
import requests

from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects

if os.name == 'nt':
    # Make the print command automatically flush in Windows. Otherwise, nothing
    # will appear until exit.
    import functools
    print = functools.partial(print, flush=True)

try:
    import htmlmin
except ImportError:
    print('''
ERROR: The minify script depends on the Python 3 module `htmlmin`. Please install it.

sudo pip3 install htmlmin

See https://htmlmin.readthedocs.io/en/latest/index.html
''', file=sys.stderr)
    raise

verbosity = 0
if os.environ.get('JEKYLL_BUILD_VERBOSITY', False) != False:
    verbosity = int(os.environ['JEKYLL_BUILD_VERBOSITY'])

def minify_html_file(name, dry_run=False):
    minifier = htmlmin.Minifier(remove_comments=True, remove_empty_space=True,
                                reduce_boolean_attributes=True)
    with open(name, 'r+', newline='\n', encoding='utf-8') as f: #encoding is needed on Windows
        minifier.input(f.read())
        f.seek(0)
        if dry_run:
            print(f'Would write file {name}.', flush=True)
        else:
            f.truncate()
            f.write(minifier.finalize())

def minify_js_file(name, dry_run=False):
    '''Currently makes http requests for minification'''
    with open(name, 'r+', newline='\n', encoding='utf-8') as f:
        contents = f.read()
        f.seek(0)
        url = 'https://www.toptal.com/developers/javascript-minifier/api/raw'
        try:
            response = requests.post(url, data={'input': contents}, timeout=20)
            response.raise_for_status()
            text = response.text
        except HTTPError as e:
            if e.response.status_code == 429: # 429 Too Many Requests
                return 429
            print(f'Error: Remote server at {url} returned this error: "{e}"! Not minified.', end=' ', flush=True)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f'Error: Remote server at {url} returned this error: "{e}"! Not minified.', end=' ', flush=True)
        else:
            if not text.startswith('// Error'):
                if dry_run:
                    print(f'Would write file {name}.', flush=True)
                else:
                    f.truncate()
                    f.write(text)
            else:
                if os.name == 'posix':
                    sys.stdout.write("\033[1;31;7m")
                print('Minification failed. File: '
                      f'{name}\nMessage:\n========\n{text}\n========',
                      end='\t\t')
                if os.name == 'posix':
                    sys.stdout.write("\033[0m")
                if verbosity <= 0:
                    print('\n', flush=True)

def parse_args():
    def directory(s):
        if not os.path.isdir(s):
            raise argparse.ArgumentTypeError('Directory not passed')
        return s

    def comma_separated_string(s):
        parts = s.split(',')

        # Make resiliant in case of stray commas at the end of config items
        while len(parts) > 0 and len(parts[-1]) == 0:
            del parts[-1]
        return tuple(parts)

    def comma_separated_extensions(s):
        return tuple('.{}'.format(i) for i in comma_separated_string(s))

    parser = argparse.ArgumentParser(description=__doc__, add_help=False,
            usage='%(prog)s ROOT <filetypes> [options]')
    required = parser.add_argument_group(title='Required')
    group = parser.add_argument_group(title='Filetypes to minify',
            description="""Only the filetypes given by these arguments will be
                minified. If you don't give any arguments in this section, this
                script won't actually do anything.""")
    options = parser.add_argument_group(title='Options')
    radd = required.add_argument
    gadd = group.add_argument
    add = options.add_argument
    root = '''The root of the tree to minify. Every .html file under the tree
        will be minified. Must be a directory'''
    starts_with = ''''A comma-separated list of strings to match filenames
        against. Any file whose basename starts with one of the strings will not
        be minified.'''
    includes = '''A comma-separated list of strings to match directory names
        against. Any directory whose name includes one of the strings anywhere
        will be skipped and none of its contents will be minified.'''
    file_includes = '''A comma-separated list of strings to search for in file
        basenames. Any file which matches one of the strings will not be
        minified.'''
    extensions = '''A comma-separated list of file extensions. Files with any of
        these extensions will be minified unless they are excluded by other
        options. If `js` is given, also minify JavaScript files having a .js
        extension. Default: html'''
    dry_run = '''Go through the motions, but don't actually write any files.'''
    html = '''Minify HTML files. If not given, HTML files will be skipped
        regardless of the other options.'''
    js = '''Minify JavaScript files. If not given, JavaScript files will be
        skipped regardless of the other options.'''

    radd('root', metavar='ROOT_DIRECTORY', type=directory, help=root)

    gadd('-H', '--html', action='store_true', help=html)
    gadd('-J', '--js', action='store_true', help=js)

    add('-e', '--extensions', metavar='STRINGS', default=('.html',),
            type=comma_separated_extensions, help=extensions)
    add('-f', '--omit-filename-starts-with', metavar='STRINGS',
            default=tuple(), type=comma_separated_string, help=starts_with)
    add('-F', '--omit-filename-includes', metavar='STRINGS', default=tuple(),
            type=comma_separated_string, help=file_includes)
    add('-d', '--omit-dirname-includes', metavar='STRINGS', default=tuple(),
            type=comma_separated_string, help=includes)
    add('-n', '--dry-run', action="store_true", help=dry_run)
    add('-h', '--help', action='help', help="Show this help message and exit.")

    return parser.parse_args()

def main():
    args = parse_args()
    for root, dirs, files in os.walk(args.root):
        if any(dirname in root for dirname in args.omit_dirname_includes):
            continue
        for file_ in files:
            if file_.startswith(args.omit_filename_starts_with):
                continue
            if any(name in file_ for name in args.omit_filename_includes):
                continue
            if file_.endswith(args.extensions):
                filename = join(root, file_)
                if filename.endswith('.js') or filename.endswith('.mjs'):
                    if args.js:
                        if verbosity == 1:
                            print(f'Minifying JavaScript file {filename}...',
                                  end=' ', flush=True)
                        result = minify_js_file(filename, args.dry_run)
                        while result == 429:
                            print(f'Rate limit hit while attempting to minify {filename}. Waiting 90 seconds before trying again...', flush=True)
                            time.sleep(90)
                            print('Wait time finished. Continuing...', flush=True)
                            result = minify_js_file(filename, args.dry_run)
                        if verbosity == 1:
                            print('Done', flush=True)
                    elif verbosity == 1:
                        print('JavaScript minification not selected so '
                              f'skipping {filename}...')
                else:
                    if args.html:
                        if verbosity == 1:
                            print(f'Minifying HTML file {filename}...', end=' ', flush=True)
                        minify_html_file(filename, args.dry_run)
                        if verbosity == 1:
                            print('Done', flush=True)
                    elif verbosity == 1:
                        print('HTML minification not selected so skipping '
                              f'{filename}...')

if __name__ == '__main__':
    main()
