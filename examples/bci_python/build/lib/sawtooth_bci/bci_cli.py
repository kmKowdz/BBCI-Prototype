# Copyright 2017 Intel Corporation
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

from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

from sawtooth_bci.bci_client import BCIClient
from sawtooth_bci.bci_exceptions import BCIException


DISTRIBUTION_NAME = 'sawtooth-bci'


# DEFAULT_URL = 'http://127.0.0.1:8008'
DEFAULT_URL = 'rest-api:8008'

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def add_create_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'create',
        help='Creates a new bci project',
        description='Sends a transaction to start an bci project with the '
        'identifier <name>. This transaction will fail if the specified '
        'project already exists.',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='unique identifier for the new project')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for project to commit')


def add_list_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'list',
        help='Displays information for all bci projects',
        description='Displays information for all bci projects in state, '
        'showing the authorized signer, the project state, and the build_no '
        'for each project.',
        parents=[parent_parser])

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')


# def add_show_parser(subparsers, parent_parser):
#     parser = subparsers.add_parser(
#         'show',
#         help='Displays information about an bci project',
#         description='Displays the bci project <name>, showing the authorized signer, '
#         'the project state, and the build_no',
#         parents=[parent_parser])

#     parser.add_argument(
#         'name',
#         type=str,
#         help='identifier for the project')

#     parser.add_argument(
#         '--url',
#         type=str,
#         help='specify URL of REST API')

#     parser.add_argument(
#         '--username',
#         type=str,
#         help="identify name of user's private key file")

#     parser.add_argument(
#         '--key-dir',
#         type=str,
#         help="identify directory of user's private key file")

#     parser.add_argument(
#         '--auth-user',
#         type=str,
#         help='specify username for authentication if REST API '
#         'is using Basic Auth')

#     parser.add_argument(
#         '--auth-password',
#         type=str,
#         help='specify password for authentication if REST API '
#         'is using Basic Auth')

def add_record_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'record',
        help='Creates a build record in an bci project',
        description='Sends a transaction for a new build instance in the '
        'bci project with the identifier <name>. This transaction will fail '
        'if the specified project does not exist.',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='identifier for the project')

    parser.add_argument(
        'build',
        type=int,
        help='build number of the project')

    parser.add_argument(
        'status',
        type=str,
        help='build status of the project')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--auth-user',
        type=str,
        help='specify username for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--auth-password',
        type=str,
        help='specify password for authentication if REST API '
        'is using Basic Auth')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for record transaction '
        'to commit')


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to update project by sending '
        'BCI transactions.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_create_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)
    # add_show_parser(subparsers, parent_parser)
    add_record_parser(subparsers, parent_parser)

    return parser


def do_list(args):
    url = _get_url(args)
    auth_user, auth_password = _get_auth_info(args)

    client = BCIClient(base_url=url, keyfile=None)

    project_list = [
        project.split(',')
        for projects in client.list(auth_user=auth_user,
                                 auth_password=auth_password)
        for project in projects.decode().split('|')
    ]

    if project_list is not None:
        fmt = "%-15s %-15.15s %-15.15s %s"
        print(fmt % ('PROJECT', 'SIGNER', 'BUILD NO', 'STATUS'))
        # fmt = "%-15s"
        # print(fmt % ('NAME'))
        for project_data in project_list:
            print(fmt % (
                project_data[0],
                project_data[1],
                project_data[2],
                project_data[3]))
    else:
        raise BCIException("Could not retrieve project listing.")


# def do_show(args):
#     name = args.name

#     url = _get_url(args)
#     auth_user, auth_password = _get_auth_info(args)

#     client = BCIClient(base_url=url, keyfile=None)

#     data = client.show(name, auth_user=auth_user, auth_password=auth_password)

#     if data is not None:

#         # build_no, project_state, auth_signer = {
#         #     name: (build_no, state, authsigner)
#         #     for name, build_no, state, authsigner in data
                
#         # }[name]


#         # {
#         #     name: (build_no, state, authsigner)
#         #     for name, build_no, state, authsigner in [
#         #         data.decode().split(',')
#         #         for project in data.decode().split('|')
#         #     ]
#         # }[name]

#         # build_no, project_state, auth_signer = {
#         #     name: (build_no, state, authsigner)
#         #     for name, build_no, state, authsigner in [
#         #         project.split(',')
#         #         for project in data.decode().split('|')
#         #     ]
#         # }[name]

#         build_no, project_state, auth_signer = {
#             name: (build_no, state, authsigner)
#             for name, build_no, state, authsigner in [
#                 data.decode().split(',')
#                 # for project in data.decode().split('|')
#             ]
#         }[name]

#         print("NAME:       : {}".format(name))
#         print("SIGNER      : {}".format(auth_signer[:6]))
#         print("BUILD NO    : {}".format(build_no))
#         print("STATE       : {}".format(project_state))
#         print("")

#     else:
#         raise BCIException("Project not found: {}".format(name))


def do_create(args):
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = BCIClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.create(
            name, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.create(
            name, auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))


def do_record(args):
    name = args.name
    build_no = args.build
    build_status = args.status

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    auth_user, auth_password = _get_auth_info(args)

    client = BCIClient(base_url=url, keyfile=keyfile)

    if args.wait and args.wait > 0:
        response = client.record(
            name, build_no, build_status, wait=args.wait,
            auth_user=auth_user,
            auth_password=auth_password)
    else:
        response = client.record(
            name, build_no, build_status,
            auth_user=auth_user,
            auth_password=auth_password)

    print("Response: {}".format(response))


def _get_url(args):
    return DEFAULT_URL if args.url is None else args.url


def _get_keyfile(args):
    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)


def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'create':
        do_create(args)
    elif args.command == 'list':
        do_list(args)
    # elif args.command == 'show':
    #     do_show(args)
    elif args.command == 'record':
        do_record(args)
    else:
        raise BCIException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except BCIException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
