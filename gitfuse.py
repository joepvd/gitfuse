#!/usr/bin/env python

import argparse
from errno import ENOENT
import logging
import os
from pathlib import Path
from time import time
import stat

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import pygit2
import yaml


class Tree(LoggingMixIn, Operations):
    def __init__(self, config):
        repo_dir = Path(config['repo']).expanduser().as_posix()
        self.repo = pygit2.Repository(repo_dir)

        self.now = time()
        self.uid = os.geteuid()
        self.gid = os.getegid()

        self.files = {}

        for checkout in config['checkouts']:
            branch = str(checkout['branch'])
            directory = str(checkout['dir'])

            tree = self.repo.revparse_single(branch).tree
            self.files[directory] = self.build_tree(tree)

    def build_tree(self, obj):
        if obj.type_str == 'blob':
            return self.repo[obj.id].read_raw()
        return {o.name: self.build_tree(o) for o in obj}

    def readdir(self, path, fh):
        return ['.', '..'] + [inode for inode in self.lookup(path)]

    def getattr(self, path, fh=None):
        attrs = {
            'st_uid': self.uid,
            'st_gid': self.gid,
            'st_ctime': self.now,
            'st_atime': self.now,
            'st_mtime': self.now,
        }

        inode = self.lookup(path)
        if isinstance(inode, bytes):
            attrs['st_mode'] = stat.S_IFREG | 0o0444
            attrs['st_nlink'] = 1
            attrs['st_size'] = len(inode)
        else:
            attrs['st_mode'] = stat.S_IFDIR | 0o0555
            attrs['st_nlink'] = len(inode)+2
            attrs['st_size'] = 4096
        return attrs

    def read(self, path, size, offset, fh):
        data = self.lookup(path)
        return data[offset:offset + size]

    def lookup(self, path):
        '''Lookup path as string
        Returns inode from self.files: Either file contents or directory entry.
        '''
        files = self.files

        inodes = [i for i in path.strip('/').split('/') if i]
        for inode in inodes:
            try:
                files = files[inode]
            except KeyError:
                raise FuseOSError(ENOENT)
        if isinstance(files, str):
            ret = inode
        else:
            ret = files
        return ret


def mount(config):
    mountpoint = Path(config['mountpoint']).expanduser()
    nothreads = config['fuse_nothreads']

    mountpoint.mkdir(parents=True, exist_ok=True)

    tree = Tree(config)

    FUSE(tree, mountpoint.as_posix(), foreground=True, nothreads=nothreads)


def main():
    default_config = Path().home().joinpath('.config', 'gitfuse', 'config.yaml').as_posix()

    parser = argparse.ArgumentParser(
        description='Mount different git branches in directories',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--config', dest='config',
        help='Specify config file',
        type=argparse.FileType('r'),
        metavar='CONFIGFILE',
        default=default_config)
    args = parser.parse_args()

    with open(args.config.name) as f:
        config = yaml.safe_load(f)

    config['fuse_nothreads'] = config.get('fuse_nothreads', False)
    if config.get('debug', False):
        logging.basicConfig(level=logging.DEBUG)

    mount(config)

if __name__ == '__main__':
    main()
