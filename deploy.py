#!/usr/bin/env python3
'''
The deploy script

Currently deploys only via rsync. To configure verbosity, set the environment
variable JEKYLL_BUILD_VERBOSITY to -1, 0, or 1, where -1 means silent, 0 means
normal, and 1 means verbose.
'''

import argparse
import jsonc as json
import os
import shlex

from subprocess import check_call, CalledProcessError

if os.name == 'nt':
    # Make the print command automatically flush in Windows. Otherwise, nothing
    # will appear until exit.
    import functools
    print = functools.partial(print, flush=True)

verbosity = 0
if os.environ.get('JEKYLL_BUILD_VERBOSITY', False) != False:
    verbosity = int(os.environ['JEKYLL_BUILD_VERBOSITY'])

class GenericContainer:
    def __str__(self):
        return '\n'.join(
            f'{repr(k)}: {repr(v)}' for k, v in sorted(self.__dict__.items()))

def make_rsync_cmd(container):
    cmd = ['rsync']
    if verbosity == 1:
        cmd += ['--verbose']
    elif verbosity == -1:
        cmd += ['--quiet']
    if container.flags:
        cmd += container.flags
    if container.exclude_file:
        cmd += ['--exclude-from', container.exclude_file]
    if container.exclude:
        for f in container.exclude:
            cmd += ['--exclude', f]
    if container.include_file:
        cmd += ['--include-from', container.include_file]
    if container.include:
        for f in container.include:
            cmd += ['--include', f]
    if container.user and container.port:
        cmd += [f"--rsh=ssh -p{container.port}"]
    if container.delete:
        cmd += ['--delete']
    local = container.site_dir
    if os.name == 'nt' and local[1] == ':':
        message = str("Windows rsync can't handle pathnames which include a "
                      "drive letter. Thus, the computed path for the site "
                      f"directory, {local}, will make rsync error out. To fix "
                      "this, make sure that your current working directory is "
                      f"in the same drive as {local}.")
        raise RuntimeError(message)
    if not local.endswith(os.path.sep) and not local.endswith('/'):
        local += os.path.sep
    remote = []
    if container.user:
        remote.append(container.user)
    remote.append(container.remote_path)
    remote = ':'.join(remote)
    cmd += [local, remote]
    return cmd

def parse_args():
    def config_file(s):
        try:
            with open(s) as f:
                return json.loads(f.read())
        except (FileNotFoundError, IsADirectoryError, json.JSONDecodeError):
            raise argparse.ArgumentTypeError(
                                    f"The file {s} isn't a valid config file!")

    def valid_directory(s):
        s = os.path.abspath(s)
        if os.path.isdir(s):
            if len(os.listdir(s)) > 0:
                return os.path.relpath(s)
            else:
                raise argparse.ArgumentTypeError(
                    "The source directory is empty! Either it isn't a valid "
                    "source directory or you haven't built the site yet.")
        else:
            raise argparse.ArgumentTypeError(
                                f"The path {s} doesn't refer to a directory!")

    parser = argparse.ArgumentParser(description=__doc__)
    add = parser.add_argument

    add(dest='source', metavar='LOCAL_SITE_SOURCE', type=valid_directory)
    add('-c', '--config', default='_deploy.jsonc', type=config_file)
    add('-n', '--dry-run', action='store_true')

    return parser.parse_args()

def main():
    args = parse_args()
    if args.config.get('method', '') != 'rsync':
        exit('Currently, the only deploy method supported is rsync. Please set '
             'the method appropriately in the deploy config file.')
    c = GenericContainer()
    c.site_dir = args.config.get('site_dir', None)
    if c.site_dir:
        print('WARNING: The site_dir setting in the config file is IGNORED. Set'
              ' it via the command line.')
    c.site_dir = args.source
    c.user = args.config.get('user', None)
    c.remote_path = args.config.get('remote_path', None)
    c.delete = args.config.get('delete', False)
    c.port = args.config.get('port', None)
    c.flags = args.config.get('flags', '-avz')
    c.exclude = args.config.get('exclude', [])
    c.include = args.config.get('include', [])
    c.exclude_file = args.config.get('exclude-from', None)
    c.include_file = args.config.get('include-from', None)
    if isinstance(c.flags, str):
        c.flags = shlex.split(c.flags)
    if isinstance(c.include, str):
        c.include = [c.include]
    if isinstance(c.exclude, str):
        c.exclude = [c.exclude]
    if verbosity == 1:
        print(c)
    cmd = make_rsync_cmd(c)
    if args.dry_run:
        print('Dry run selected.')
    if verbosity >= 0:
        if c.user:
            print(f'Deploying to {c.user}...')
        else:
            print('Deploying...')
    if verbosity == 1 or args.dry_run:
        print('Executing the rsync command: ' + str(cmd))
    try:
        if args.dry_run:
            cmd.insert(1, '--dry-run')
        check_call(cmd)
    except CalledProcessError as e:
        print(f'Error running rsync: rsync exited with status {e.returncode}')
        exit(32)
    else:
        if verbosity == 1:
            print('rsync completed successfully')
        exit(0)

if __name__ == '__main__':
    main()
