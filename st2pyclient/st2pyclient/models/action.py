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


from st2pyclient.models.base import Model
from st2pyclient.models.ref import ContentReference


class Action(Model):

    def __init__(self, pack, name, runner_type, entry_point=None,
                 enabled=True, parameters=None, notify=None):
        self._pack = pack
        self._name = name
        self._ref = ContentReference(pack=pack, name=name).ref
        self._runner_type = runner_type
        self._entry_point = entry_point
        self._enabled = enabled
        self._parameters = parameters
        self._notify = notify

    @property
    def pack(self):
        return self._pack

    @property
    def name(self):
        return self._name

    @property
    def ref(self):
        return self._ref

    @property
    def runner_type(self):
        return self._runner_type

    @property
    def entry_point(self):
        return self._entry_point

    @property
    def enabled(self):
        return self._enabled

    @property
    def parameters(self):
        return self._parameters

    @property
    def notify(self):
        return self._notify
