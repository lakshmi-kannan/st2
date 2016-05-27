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


class Client(object):

    def __init__(self, auth_base_url=None, auth_api_version='v1', auth_credentials=None,
                 api_base_url=None, api_version='v1', creds_file_path='~/.st2/config',
                 debug=False):

    def __init__(self, user=None, pass=None, api_key=None, api_base_url=None,
                 auth_base_url=None, debug=False, creds_file_path='~/.st2.config'):
        pass


           if not self._auth_credentials:
            self._auth_credentials = self._get_credentials_from_file(creds_file_path)
