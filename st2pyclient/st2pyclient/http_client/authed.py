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

import logging

from st2pyclient.http_client.base import BaseClient
from st2pyclient.http_client.token import TokenClient

LOG = logging.getLogger(__name__)


class AuthedClient(BaseClient):

    def __init__(self, user=None, password=None, api_key=None,
                 auth_base_url=None, auth_api_version='v1',
                 api_base_url=None, api_version='v1', debug=False):
        self._auth_base_url = auth_base_url
        self._auth_api_version = auth_api_version
        self._user = user
        self._password = password
        self._api_key = api_key
        self._api_base_url = api_base_url
        self._api_version = api_version
        if self._api_key:
            self._is_api_key_auth = True
            self._api_key_headers = {'St2-Api-Key': self._api_key}
        else:
            self._is_token_auth = True
            self._token_client = TokenClient(
                auth_base_url=auth_base_url,
                auth_api_version=auth_api_version,
                user=user,
                password=password
            )
        self._debug = debug

    def post(self, relative_url, payload, debug=False):
        super(AuthedClient, self).post(relative_url, payload,
                                       headers=self._get_auth_headers(),
                                       debug=self._debug or debug)

    def get(self, relative_url, payload=None, debug=False):
        super(AuthedClient, self).get(relative_url, payload=payload,
                                      headers=self._get_auth_headers(),
                                      debug=self._debug or debug)

    def put(self, relative_url, payload, debug=False):
        super(AuthedClient, self).put(relative_url, payload,
                                      headers=self._get_auth_headers(),
                                      debug=self._debug or debug)

    def delete(self, relative_url, debug=False):
        super(AuthedClient, self).delete(relative_url,
                                         headers=self._get_auth_headers(),
                                         debug=self._debug or debug)

    def _get_auth_headers(self):
        if self._is_api_key_auth:
            return self._api_key_headers

        try:
            return {'X-Auth-Token': self._token_client.get_token()}
        except:
            LOG.exception('Failed negotiating auth token with st2!')
            raise

    @staticmethod
    def _is_token_expired(token):
        pass
