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

import hashlib

from sawtooth_sdk.processor.exceptions import InternalError


XO_NAMESPACE = hashlib.sha512('xo'.encode("utf-8")).hexdigest()[0:6]


def _make_xo_address(name):
    return XO_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]


class Project:
    def __init__(self, name, build_no, build_status, auth_signer):
        self.name = name
        self.build_no = build_no
        self.build_status = build_status
        self.auth_signer = auth_signer

class XoState:

    TIMEOUT = 3

    def __init__(self, context):
        """Constructor.

        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
        """

        self._context = context
        self._address_cache = {}

    def set_project(self, project_name, project):
        """Store the project in the validator state.

        Args:
            project_name (str): The name.
            project (Project): The information specifying the current project.
        """

        projects = self._load_projects(project_name=project_name)

        projects[project_name] = project

        self._store_project(project_name, projects=projects)

    def get_project(self, project_name):
        """Get the project associated with project_name.

        Args:
            project_name (str): The name.

        Returns:
            (Project): All the information specifying a project.
        """

        return self._load_projects(project_name=project_name).get(project_name)

    def _store_project(self, project_name, projects):
        address = _make_xo_address(project_name)

        state_data = self._serialize(projects)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _load_projects(self, project_name):
        address = _make_xo_address(project_name)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_projects = self._address_cache[address]
                projects = self._deserialize(serialized_projects)
            else:
                projects = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                projects = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                projects = {}

        return projects

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python
        Project objects.

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): project name (str) keys, Project values.
        """

        projects = {}
        try:
            for project in data.decode().split("|"):
                name, build_no, build_status, auth_signer = project.split(",")

                projects[name] = Project(
                    name,
                    build_no,
                    build_status,
                    auth_signer)
        except ValueError as e:
            raise InternalError("Failed to deserialize project data") from e

        return projects

    def _serialize(self, projects):
        """Takes a dict of project objects and serializes them into bytes.

        Args:
            projects (dict): project name (str) keys, Project values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        project_strs = []
        for name, p in projects.items():
            proj_str = ",".join(
                [name, p.build_no, p.build_status, p.auth_signer])
            project_strs.append(proj_str)

        return "|".join(sorted(project_strs)).encode()
