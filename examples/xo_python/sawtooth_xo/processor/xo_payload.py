# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class XoPayload:

    def __init__(self, payload):
        try:
            # The payload is csv utf-8 encoded string
            name, action, build_no, build_status = payload.decode().split(",")
        except ValueError as e:
            raise InvalidTransaction("Invalid payload serialization") from e

        if not name:
            raise InvalidTransaction('Name is required')

        if '|' in name:
            raise InvalidTransaction('Name cannot contain "|"')

        if not action:
            raise InvalidTransaction('Action is required')

        if action not in ('create', 'record', 'list'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        if action == 'record':
            try:

                if int(build_no) not in range(1, 1000):
                    raise InvalidTransaction(
                        "Build Number must be an integer")
            except ValueError:
                raise InvalidTransaction(
                    'Build Number must be an integer') from ValueError

        if action == 'record':
            build_no = int(build_no)

        self._name = name
        self._action = action
        self._build_no = build_no
        self._build_status = build_status

    @staticmethod
    def from_bytes(payload):
        return XoPayload(payload=payload)

    @property
    def name(self):
        return self._name

    @property
    def action(self):
        return self._action

    @property
    def build_no(self):
        return self._build_no

    @property
    def build_status(self):
        return self._build_status
