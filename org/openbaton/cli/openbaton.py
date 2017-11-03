#!/usr/bin/env python

from __future__ import print_function

import argparse
import getpass
import json
import logging.config
import os
import sys

import tabulate
import texttable
from requests import ConnectionError

from org.openbaton.cli.agents.agents import OpenBatonAgentFactory
from org.openbaton.cli.errors.errors import WrongCredential, WrongParameters, NfvoException, NotFoundException

logger = logging.getLogger("org.openbaton.cli.MainAgent")

ACTIONS = ["list", "show", "delete", "create"]

LIST_PRINT_KEY = {
    "nsd": ["id", "name", "vendor", "version"],
    "vnfd": ["id", "name", "vendor", "version"],
    "nsr": ["id", "name", "status", "task", "vendor", "version", ],
    "vnfr": ["id", "name", "vendor", "version", "status"],
    "vim": ["id", "name", "authUrl", "tenant", "username"],
    "project": ["id", "name", "description"],
    "event": ["id", "name", "networkServiceId", "virtualNetworkFunctionId", "type", "endpoint"],
    "vnfpackage": ["id", "name"],
    "csarnsd": ["id", "name"],
    "vnfci": ["id", "name"],
    "csarvnfd": ["id", "name"],
    "key": ["id", "name", "fingerprint"],
    "log": ["id"],
    "vdu": ["id", "name"],
    "user": ["id", "username", "email"],
    "market": ["id", "name", "vendor", "version"],
    "service": ["id", "name"],
}

SHOW_EXCLUDE_KEY = {
    "nsd": [],
    "vnfd": [],
    "nsr": [],
    "vnfr": [],
    "vim": ["password"],
    "project": [],
    "event": ["version"],
    "vnfpackage": [],
    "csarnsd": [],
    "csarvnfd": [],
    "market": [],
    "key": [],
    "log": [],
    "vdu": [],
    "vnfci": [],
    "user": ["password"],
    "service": [],
}

UNSUPPORTED_ACTIONS = {
    "nsd": [],
    "vnfd": [],
    "nsr": [],
    "vnfr": [],
    "vim": [],
    "project": [],
    "event": [],
    "vnfci": ["list"],
    "vdu": ["list", "create", "delete"],
    "vnfpackage": [],
    "csarnsd": ["list", "show", "delete"],
    "csarvnfd": ["list", "show", "delete"],
    "market": ["list", "show", "delete"],
    "key": [],
    "log": ["list", "delete", "create"],
    "user": [],
    "service": ["show"],
}


def _handle_params(agent_choice, action, params):
    if agent_choice == 'vnfci':
        if action == 'create':
            if len(params) < 3:
                raise WrongParameters(
                    "usage: openbaton vnfci create <vnfcomponent> <nsr_id> <vnfr_id> [vdu_id [standby]] ")
            if len(params) == 5:  # <vnfcomponent> <nsr_id> <vnfr_id> <vdu_id> standby
                if params[4] == 'standby':
                    return params[0:4] + [True]
                else:
                    raise WrongParameters(
                        "usage: openbaton vnfci create <vnfcomponent> <nsr_id> <vnfr_id> [vdu_id [standby]] ")
            if len(
                    params) == 4:  # <vnfcomponent> <nsr_id> <vnfr_id> standby    or   <vnfcomponent> <nsr_id> <vnfr_id> <vdu_id>
                if params[3] == 'standby':
                    return params[0:3] + ['', True]
        if action == 'delete':
            if len(params) < 2:
                raise WrongParameters('usage: openbaton vnfci delete <nsr_id> <vnfr_id> [vdu_id [vnfci_id]]')

    return params


def _exec_action(factory, agent_choice, action, project_id, params):
    try:
        if action not in ACTIONS:
            print("Action %s unknown" % action)
            exit(1)
        if agent_choice not in LIST_PRINT_KEY.keys():
            print("agent %s unknown" % agent_choice)
            exit(1)
        if action in UNSUPPORTED_ACTIONS.get(agent_choice):
            print("{} agent does not support {} action".format(agent_choice, action))
            exit(1)
        if action == "list":
            ag = factory.get_agent(agent_choice, project_id=project_id)
            tabulate_tabulate = tabulate.tabulate(get_result_as_list_find_all(ag.find(), agent_choice),
                                                  headers=LIST_PRINT_KEY.get(agent_choice), tablefmt="grid")
            print(" ")
            print(tabulate_tabulate)
            print(" ")
        if action == "delete":
            params = _handle_params(agent_choice, action, params)
            if len(params) <= 0:
                print("Delete takes one argument, the id")
                exit(1)
            factory.get_agent(agent_choice, project_id=project_id).delete(*params)
            print("Executed delete.")
        if action == "show":
            if len(params) != 0:
                if isinstance(params, str):
                    params = params.split()
            else:
                print("Show takes one argument, the id")
                exit(1)
            table = texttable.Texttable()
            table.set_cols_align(["l", "r"])
            table.set_cols_valign(["c", "b"])
            table.set_cols_dtype(['t', 't'])
            params = _handle_params(agent_choice, action, params)
            table.add_rows(
                get_result_to_show(factory.get_agent(agent_choice, project_id=project_id).find(*params),
                                   agent_choice))
            print(" ")
            print(table.draw() + "\n")
            print(" ")
        if action == "create":
            if len(params) <= 0:
                print("create takes one argument, the object to create")
                exit(1)
            table = texttable.Texttable()
            table.set_cols_align(["l", "r"])
            table.set_cols_valign(["c", "b"])
            table.set_cols_dtype(['t', 't'])
            params = _handle_params(agent_choice, action, params)
            table.add_rows(
                get_result_to_show(factory.get_agent(agent_choice, project_id=project_id).create(*params),
                                   agent_choice))
            print("\n")
            print(table.draw() + "\n\n")
    except WrongCredential as e:
        print("")
        print("ERROR: %s" % e.message)
        print("")
    except WrongParameters as e:
        print("")
        print("ERROR: %s" % e.message)
        print("")
    except ConnectionError as e:
        print("")
        print("ERROR: %s" % e.message)
        print("")
    except NfvoException as e:
        print("")
        print("ERROR: %s" % e.message)
        print("")
    except NotFoundException as e:
        print("")
        print("ERROR: %s" % e.message)
        print("")


def get_result_to_show(obj, agent_choice):
    if isinstance(obj, str) or type(obj) == unicode:
        if not obj:
            exit(0)
        try:
            obj = json.loads(obj)
        except ValueError:
            print(obj)
            exit(0)
    if isinstance(obj, list):
        for item in obj:
            print(item)
        exit(0)
    elif isinstance(obj, dict):
        result = [["key", "value"]]
        for k, v in obj.items():
            if k not in SHOW_EXCLUDE_KEY.get(agent_choice):
                if isinstance(v, list):
                    if len(v) > 0:
                        tmp = []
                        if isinstance(v[0], dict):
                            tmp.append(" value: \n")
                            tmp.extend(["- " + (x.get('ip') or x.get("id")) for x in v])
                        result.append([k, "\n".join(tmp)])
                else:
                    if isinstance(v, dict):
                        idName = v.get("name")
                        if idName is None:
                            idName = v.get("id")
                        result.append([k, idName])
                    else:
                        result.append([k, v])

        return result


def get_result_as_list_find_all(start_list, agent):
    res = []
    for x in json.loads(start_list):
        tmp = []
        for key in LIST_PRINT_KEY.get(agent):
            tmp.append(x.get(key))
        res.append(tmp)
    return res


def openbaton(agent_choice, action, params, project_id, username, password, nfvo_ip, nfvo_port, https=False):
    factory = OpenBatonAgentFactory(nfvo_ip=nfvo_ip,
                                    nfvo_port=nfvo_port,
                                    https=https,
                                    version=1,
                                    username=username,
                                    password=password,
                                    project_id=project_id)

    _exec_action(factory, agent_choice, action, project_id, params)


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-pid", "--project-id", help="the project-id to use")
    parser.add_argument("-u", "--username", help="the openbaton username")
    parser.add_argument("-p", "--password", help="the openbaton password")
    parser.add_argument("-d", "--debug", help="show debug prints", action="store_true")
    parser.add_argument("-ip", "--nfvo-ip", help="the openbaton nfvo ip")
    parser.add_argument("--nfvo-port", help="the openbaton nfvo port")
    parser.add_argument("-s", "--ssl", help="use HTTPS instead of HTTP", action="store_true")

    parser.add_argument("agent",
                        help="the agent you want to use. Possibilities are: \n" + str(SHOW_EXCLUDE_KEY.keys()),
                        choices=SHOW_EXCLUDE_KEY.keys())
    parser.add_argument("action",
                        help="the action you want to call. Possibilities are: \n" + str(ACTIONS),
                        choices=ACTIONS)
    parser.add_argument("params", help="The id, file or json", nargs='*')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        print()
    else:
        logging.basicConfig(level=logging.WARNING)

    project_id = None
    username = None
    password = None
    nfvo_ip = None
    nfvo_port = None

    project_id = os.environ.get('OB_PROJECT_ID')
    username = os.environ.get('OB_USERNAME')
    password = os.environ.get('OB_PASSWORD')
    nfvo_ip = os.environ.get('OB_NFVO_IP')
    nfvo_port = os.environ.get('OB_NFVO_PORT')

    if args.username is not None:
        username = args.username
    if args.password is not None:
        password = args.password
    if args.nfvo_ip is not None:
        nfvo_ip = args.nfvo_ip
    if args.nfvo_port is not None:
        nfvo_port = args.nfvo_port
    if args.project_id is not None:
        project_id = args.project_id
    ssl_enabled = args.ssl

    if project_id is None:
        if sys.version_info[0] < 3:
            project_id = raw_input("insert project-id: ")
        else:
            project_id = input("insert project-id: ")
    if username is None or username == "":
        if sys.version_info[0] < 3:
            username = raw_input("insert user: ")
        else:
            username = input("insert user: ")
    if password is None or password == "":
        password = getpass.getpass("insert password: ")
    if nfvo_ip is None or nfvo_ip == "":
        if sys.version_info[0] < 3:
            nfvo_ip = raw_input("insert nfvo_ip: ")
        else:
            nfvo_ip = input("insert nfvo_ip: ")
    if nfvo_port is None or nfvo_port == "":
        if sys.version_info[0] < 3:
            nfvo_port = raw_input("insert nfvo_port: ")
        else:
            nfvo_port = input("insert nfvo_port: ")

    logger.debug("username '%s'" % username)
    logger.debug("project_id '%s'" % project_id)
    logger.debug("nfvo_ip '%s'" % nfvo_ip)
    logger.debug("nfvo_port '%s'" % nfvo_port)

    if nfvo_port is None or nfvo_port == "":
        print("")
        print("Error: nfvo_port is empty")
        print("")
        exit(2)

    if nfvo_ip is None or nfvo_ip == "":
        print("")
        print("Error: nfvo_ip is empty")
        print("")
        exit(2)

    if username is None or password is None or username == "" or password == "":
        print("")
        print("Error: username and/or password are empty")
        print("")
        exit(2)

    if project_id is None or project_id == "":
        logger.warning("The project id is missing. Run openbaton project list for choosing a project id")

    openbaton(args.agent, args.action, params=args.params, project_id=project_id, username=username, password=password,
              nfvo_ip=nfvo_ip, nfvo_port=nfvo_port, https=ssl_enabled)


if __name__ == '__main__':
    print("Open Baton fancy CLI :)")
