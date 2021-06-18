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

from sawtooth_bci.processor.bci_payload import BCIPayload
from sawtooth_bci.processor.bci_state import Project
from sawtooth_bci.processor.bci_state import BCIState
from sawtooth_bci.processor.bci_state import BCI_NAMESPACE

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError


LOGGER = logging.getLogger(__name__)


class BCITransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return 'bci'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [BCI_NAMESPACE]

    def apply(self, transaction, context):

        header = transaction.header
        signer = header.signer_public_key

        bci_payload = BCIPayload.from_bytes(transaction.payload)

        bci_state = BCIState(context)

        if bci_payload.action == 'create':

            if bci_state.get_project(bci_payload.name) is not None:
                raise InvalidTransaction(
                    'Invalid action: Project already exists: {}'.format(
                        bci_payload.name))

            project = Project(name=bci_payload.name,
                        build_no="",
                        build_status="",
                        auth_signer="")

            bci_state.set_project(bci_payload.name, project)
            _display("Signer {} created a project.".format(signer[:6]))

        elif bci_payload.action == 'record':
            project = bci_state.get_project(bci_payload.name)

            if project is None:
                raise InvalidTransaction(
                    'Invalid action: Record action requires an '
                    'existing project')

            if project.build_status in ('SUCCESS', 'FAILURE'):
                raise InvalidTransaction('Invalid Action: Build status '
                    'already recorded.')

            if project.auth_signer != signer:
                raise InvalidTransaction('Invalid Action: Record action '
                    'requires an authorized signer')

            if project.build_no != '':
                raise InvalidTransaction(
                    'Invalid Action: Build Number {} already exist'.format(
                        bci_payload))

            # if project.state != '':
            #     raise InvalidTransaction(
            #         'Invalid Action: Build record already exist')

            if project.auth_signer == '':
                project.auth_signer = signer

            if project.build_no == '':
                project.build_no = bci_payload.build_no

            if project.build_status == '':
                project.build_status = bci_payload.build_status

            bci_state.set_project(bci_payload.name, project)

            _display(
                _project_data_to_str(
                    project.build_no,
                    project.build_status,
                    project.auth_signer,
                    bci_payload.name))
            # _display(
            #     "Authorized signer {} records a build.\n\n".format(
            #         signer[:6])
            #     + _project_data_to_str(
            #         project.build_no,
            #         project.state,
            #         project.auth_signer,
            #         bci_payload.name))

        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                bci_payload.action))


def _project_data_to_str(build_no, build_status, auth_signer, name):
    msg = "\n"
    msg += "NAME: {}\n".format(name)
    msg += "SIGNER: {}\n".format(auth_signer[:6])
    msg += "BUILD NO: {}\n".format(build_no)
    msg += "STATUS: {}\n".format(build_status)
    msg += "\n"
    return msg


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        # length = max(len(line) for line in msg)
    else:
        # length = len(msg)
        msg = [msg]

    for line in msg:
        LOGGER.debug(line)
    # pylint: disable=logging-not-lazy
    # LOGGER.debug("+" + (length + 2) * "-" + "+")
    # for line in msg:
        # LOGGER.debug("+ " + line.center(length) + " +")
    # LOGGER.debug("+" + (length + 2) * "-" + "+")
