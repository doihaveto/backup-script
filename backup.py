import os
import errno
import subprocess
from time import time
from pathlib import Path
from datetime import timedelta

backup_path = '/mnt/p/backup'
full_backup_path = '/mnt/p/backup/full_backup.txt'
backup_structure_path = '/mnt/p/backup/backup_structure.txt'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def parse_source_dst(src, dst):
    src = src[0].lower() + '/' + src[2:].replace('\\', '/')
    if not src.endswith('/'):
        src += '/'
    src_unixpath = '/mnt/' + src[0] + src[2:]
    src_tpath = src.replace(':', '')
    dst = os.path.join(dst, src_tpath)
    return src_unixpath, dst

def sync_structure(src, backup_dst, max_depth=0):
    print('Structure:', src)
    start = time()
    src, _ = parse_source_dst(src, backup_dst)
    if os.path.exists(src):
        depth = 1
        for path, dirs, files in os.walk(src):
            if max_depth and max_depth > depth:
                break
            for dir_name in dirs:
                dst = os.path.join(backup_dst, os.path.join(path, dir_name)[5:])
                if not os.path.isdir(dst):
                    if not os.path.exists(dst):
                        os.makedirs(dst)
                    else:
                        os.unlink(dst)
                        os.makedirs(dst)
            for fname in files:
                dst = os.path.join(backup_dst, os.path.join(path, fname)[5:])
                if not os.path.isfile(dst):
                    if not os.path.exists(dst):
                        Path(dst).touch()
                    else:
                        os.unlink(dst)
                        Path(dst).touch()
            depth += 1
        delta = timedelta(seconds=time() - start)
        print('Finished in ', delta)

def rsync_root(src, dst, mode):
    print('Full:', src)
    start = time()
    src, dst = parse_source_dst(src, dst)
    if os.path.exists(src):
        mkdir_p(dst)
        cmd = ['rsync']
        if mode == 'r':
            cmd.append('-r')
        cmd += [src, dst]
        subprocess.run(cmd)
        delta = timedelta(seconds=time() - start)
        print('Finished in ', delta)


if __name__ == '__main__':
    with open(full_backup_path) as f:
        full_backup = [x.strip() for x in f.readlines() if x.strip() and not x.strip().startswith('#')]
    with open(backup_structure_path) as f:
        backup_structure = [x.strip() for x in f.readlines() if x.strip() and not x.strip().startswith('#')]
    for src_line in full_backup:
        mode, src = src_line.split(' ', 1)
        rsync_root(src.strip(), backup_path, mode)
    for src_line in backup_structure:
        mode, src = src_line.split(' ', 1)
        max_depth = 0
        if mode.startswith('d'):
            max_depth = int(mode[1:])
        sync_structure(src, backup_path, max_depth=max_depth)
