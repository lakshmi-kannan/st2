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

from st2pyclient.exceptions.general import InvalidContentReferenceError

PACK_SEPARATOR = '.'


class ContentReference(object):
    """
    Class used for referring to resources which belong to a content pack.
    """
    def __init__(self, pack=None, name=None):
        self.pack = self.validate_pack_name(pack=pack)
        self.name = name
        self.ref = self.to_string_reference(pack=pack, name=name)

    @staticmethod
    def is_resource_reference(ref):
        """
        This method uses a very naive approach to determine if the provided
        string is a resource reference - it only checks if this string contains
        a separator.

        :rtype ref: ``str``
        """
        return PACK_SEPARATOR in ref

    @staticmethod
    def from_string_reference(ref):
        pack = ContentReference.get_pack(ref)
        name = ContentReference.get_name(ref)

        return ContentReference(pack=pack, name=name)

    @staticmethod
    def to_string_reference(pack=None, name=None):
        if pack and name:
            pack = ContentReference.validate_pack_name(pack=pack)
            return PACK_SEPARATOR.join([pack, name])
        else:
            raise ValueError('Both pack and name needed for building ref. pack=%s, name=%s' %
                             (pack, name))

    @staticmethod
    def validate_pack_name(pack):
        if PACK_SEPARATOR in pack:
            raise ValueError('Pack name should not contain "%s"' % (PACK_SEPARATOR))

        return pack

    @staticmethod
    def get_pack(ref):
        try:
            return ref.split(PACK_SEPARATOR, 1)[0]
        except (IndexError, AttributeError):
            raise InvalidContentReferenceError(ref=ref)

    @staticmethod
    def get_name(ref):
        try:
            return ref.split(PACK_SEPARATOR, 1)[1]
        except (IndexError, AttributeError):
            raise InvalidContentReferenceError(ref=ref)

    def __repr__(self):
        return ('<ContentReference pack=%s,name=%s,ref=%s>' %
                (self.pack, self.name, self.ref))
