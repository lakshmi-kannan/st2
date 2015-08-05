# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid

import eventlet

from st2common import log as logging
from st2common.ssh.paramiko_ssh import ParamikoSSHClient
import st2common.util.jsonify as jsonify

LOG = logging.getLogger(__name__)


class ParallelSSHClient(object):
    KEYS_TO_TRANSFORM = ['stdout', 'stderr']

    def __init__(self, user, pkey, hosts, port=22, concurrency=10,
                 raise_on_error=False, connect=True):
        self._ssh_user = user
        self._ssh_key = pkey
        self._hosts = hosts
        self._ssh_port = port

        if not hosts:
            raise Exception('Need an non-empty list of hosts to talk to.')

        self._pool = eventlet.GreenPool(concurrency)
        self._hosts_client = {}
        self._bad_hosts = []
        self._scan_interval = 0.1
        if connect:
            self.connect(raise_on_error=raise_on_error)

    def connect(self, raise_on_error=False):
        for host in self._hosts:
            LOG.debug('Connecting to host: %s as user: %s and key: %s', host, self._ssh_user,
                      self._ssh_key)
            client = ParamikoSSHClient(host, username=self._ssh_user,
                                       key=self._ssh_key, port=self._ssh_port)
            try:
                client.connect()
            except:
                LOG.exception('Failed connecting to host: %s')
                if raise_on_error:
                    raise
                self._bad_hosts.append(host)
            else:
                self._hosts_client[host + ':' + str(uuid.uuid4())] = client

    def run(self, cmd, timeout=None, cwd=None):
        results = {}
        for host in self._bad_hosts:
            results[host] = {
                'error': 'Failed connecting to host.',
                'succeeded': False,
                'failed': True
            }

        # Note that doing a chdir using sftp client in ssh_client doesn't really
        # set the session working directory. So we have to do this hack.
        if cwd:
            cmd = 'cd %s && %s' % (cwd, cmd)

        for host in self._hosts_client.keys():
            while not self._pool.free():
                eventlet.sleep(self._scan_interval)
            self._pool.spawn(self._run_command, cmd=cmd, host=host.split(':')[0],
                             results=results, timeout=timeout, result_key=host)

        self._pool.waitall()
        return jsonify.json_loads(results, ParallelSSHClient.KEYS_TO_TRANSFORM)

    def put(self, local_path, remote_path, mode=None, mirror_local_mode=False):
        results = {}

        if not os.path.exists(local_path):
            raise Exception('Local path %s does not exist.' % local_path)

        for host in self._hosts_client.keys():
            while not self._pool.free():
                eventlet.sleep(self._scan_interval)
            self._pool.spawn(self._put_files, local_path=local_path,
                             remote_path=remote_path,
                             host=host,
                             results=results, mode=mode, mirror_local_mode=mirror_local_mode)
        self._pool.waitall()
        return results

    def _run_command(self, host, cmd, results, timeout=None, result_key=None):
        try:
            LOG.debug('Running command: %s on host: %s.', cmd, host)
            client = self._hosts_client[result_key]
            (stdout, stderr, exit_code) = client.run(cmd, timeout=timeout)
            is_succeeded = (exit_code == 0)
            if not result_key:
                result_key = host
            results[result_key] = {'stdout': stdout, 'stderr': stderr, 'exit_code': exit_code,
                                   'succeeded': is_succeeded, 'failed': not is_succeeded}
        except:
            LOG.exception('Failed executing command %s on host %s', cmd, host)

    def delete(self, path):
        results = {}

        for host in self._hosts_client.keys():
            while not self._pool.free():
                eventlet.sleep(self._scan_interval)
            self._pool.spawn(self._delete_files, host=host, path=path, results=results)

        self._pool.waitall()
        return results

    def close(self):
        for host in self._hosts_client.keys():
            try:
                self._hosts_client[host].close()
            except:
                LOG.exception('Failed shutting down SSH connection to host: %s', host)

    def _put_files(self, local_path, remote_path, host, results, mode=None,
                   mirror_local_mode=False):
        try:
            LOG.debug('Copying file to host: %s' % host)
            if os.path.isdir(local_path):
                result = self._hosts_client[host].put_dir(local_path, remote_path)
            else:
                result = self._hosts_client[host].put(local_path, remote_path,
                                                      mirror_local_mode=mirror_local_mode,
                                                      mode=mode)
            LOG.debug('Result of copy: %s' % result)
            results[host] = result
        except:
            LOG.exception('Failed sending file(s) in path %s to host %s', local_path, host)

    def _delete_files(self, host, path, results):
        try:
            result = self._hosts_client[host].delete(host, path)
            results[host] = result
        except:
            LOG.exception('Failed deleting file(s) in path %s on host %s.', path, host)
