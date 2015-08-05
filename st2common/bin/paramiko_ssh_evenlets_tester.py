#!/usr/bin/env python2.7

import argparse
import os
import pprint
import sys

import eventlet

from st2common.ssh.parallel_ssh import ParallelSSHClient

eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=False if '--use-debugger' in sys.argv else True,
    time=True)


def main(user, password, pkey, hosts_str, cmd, file_path, dir_path, repeat):
    hosts = hosts_str.split(",")
    if repeat:
        hosts_list = []
        for i in range(repeat):
            hosts_list.extend(hosts)
        hosts = hosts_list

    client = ParallelSSHClient(user=user, pkey=pkey, password=password, hosts=hosts)
    pp = pprint.PrettyPrinter(indent=4)

    if file_path:
        if not os.path.exists(file_path):
            raise Exception('File not found.')
        results = client.put(file_path, '/home/lakshmi/test_file', mode="0660")
        pp.pprint('Copy results: \n%s' % results)
        results = client.run('ls -rlth')
        pp.pprint('ls results: \n%s' % results)

    if dir_path:
        if not os.path.exists(dir_path):
            raise Exception('File not found.')
        results = client.put(dir_path, '/home/lakshmi/', mode="0660")
        pp.pprint('Copy results: \n%s' % results)
        results = client.run('ls -rlth')
        pp.pprint('ls results: \n%s' % results)

    if cmd:
        results = client.run(cmd, cwd='/tmp')
        print('Command was: %s' % cmd)
        print('Results:\n\n')
        pp.pprint(results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parallel SSH tester.')
    parser.add_argument('--hosts', required=True,
                        help='List of hosts to connect to')
    parser.add_argument('--repeat', required=False, type=int,
                        help='Number of times to repeat the host.')
    parser.add_argument('--private-key', required=False,
                        help='Private key to use.')
    parser.add_argument('--password', required=False,
                        help='Password.')
    parser.add_argument('--user', required=True,
                        help='SSH user name.')
    parser.add_argument('--cmd', required=False,
                        help='Command to run on host.')
    parser.add_argument('--file', required=False,
                        help='Path of file to copy to remote host.')
    parser.add_argument('--dir', required=False,
                        help='Path of dir to copy to remote host.')
    args = parser.parse_args()

    main(user=args.user, pkey=args.private_key, password=args.password,
         hosts_str=args.hosts, cmd=args.cmd,
         file_path=args.file, dir_path=args.dir, repeat=args.repeat)
