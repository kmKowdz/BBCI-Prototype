# Copyright 2016-2018 Intel Corporation
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
# ------------------------------------------------------------------------------

import logging

from sawtooth_xo.processor.xo_payload import XoPayload
from sawtooth_xo.processor.xo_state import Project
from sawtooth_xo.processor.xo_state import XoState
from sawtooth_xo.processor.xo_state import XO_NAMESPACE

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError


LOGGER = logging.getLogger(__name__)


class XoTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return 'xo'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [XO_NAMESPACE]

    def apply(self, transaction, context):

        header = transaction.header
        signer = header.signer_public_key

        xo_payload = XoPayload.from_bytes(transaction.payload)

        xo_state = XoState(context)

        if xo_payload.action == 'create':

            if xo_state.get_project(xo_payload.name) is not None:
                raise InvalidTransaction(
                    'Invalid action: Project already exists: {}'.format(
                        xo_payload.name))

            project = Project(name=xo_payload.name,
                        build_no="",
                        state="",
                        auth_signer="")

            xo_state.set_project(xo_payload.name, project)
            _display("Signer {} created a project.".format(signer[:6]))

        elif xo_payload.action == 'record':
            project = xo_state.get_project(xo_payload.name)

            if project is None:
                raise InvalidTransaction(
                    'Invalid action: Record action requires an existing project')

            if project.state in ('SUCCESS', 'FAILURE'):
                raise InvalidTransaction('Invalid Action: Build record already exist.')

            if (project.auth_signer != signer):
                raise InvalidTransaction('Invalid Action: Record action requires an authorized signer')

            if project.build_no != '':
                raise InvalidTransaction(
                    'Invalid Action: Build Number {} already exist'.format(
                        xo_payload))

            if project.auth_signer == '':
                project.auth_signer = signer

            if project.build_no == '':
                project.build_no = xo_payload.build_no
            
            if project.state == '':
                project.state = xo_payload.state

            xo_state.set_project(xo_payload.name, project)
            _display(
                "Authorized signer {} records a build.\n\n".format(
                    signer[:6])
                + _project_data_to_str(
                    project.build_no,
                    project.state,
                    project.auth_signer,
                    xo_payload.name))

        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                xo_payload.action))


def _project_data_to_str(build_no, state, auth_signer, name):
    out = ""
    out += "NAME: {}\n".format(name)
    out += "SIGNER: {}\n".format(auth_signer[:6])
    out += "BUILD NO: {}\n".format(build_no)
    out += "STATE: {}\n".format(state)
    out += "\n"
    return out


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    # pylint: disable=logging-not-lazy
    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")
