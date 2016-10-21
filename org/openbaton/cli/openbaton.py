#!/usr/bin/env python

from __future__ import print_function

import texttable
import getpass
import json
import logging.config
import os
import tabulate
import argparse

from org.openbaton.cli.agents.agents import MainAgent

logger = logging.getLogger("org.openbaton.cli.MainAgent")

ACTIONS = ["list", "show", "delete", "create"]

LIST_PRINT_KEY = {
    "nsd": ["id", "name", "vendor", "version"],
    "nsr": ["id", "name", "status", "task", "vendor", "version", ],
    "vim": ["id", "name", "authUrl", "tenant", "username"],
    "project": ["id", "name", "description"],
    "vnfpackage": ["id", "name"],
    "user": ["id", "username", "email"],
}

SHOW_EXCLUDE_KEY = {
    "nsd": [],
    "nsr": [],
    "vim": ["password"],
    "project": [],
    "vnfpackage": [],
    "user": ["password"]
}


def exec_action(agent, agent_choice, action, project_id, *args):
    if action not in ACTIONS:
        print("Action %s unknown" % action)
        exit(1)
    if agent_choice not in LIST_PRINT_KEY.keys():
        print("agent %s unknown" % agent_choice)
        exit(1)
    if action == "list":
        ag = agent.get_agent(agent_choice, project_id=project_id)
        tabulate_tabulate = tabulate.tabulate(get_result_as_list_find_all(ag.find(), agent_choice),
                                              headers=LIST_PRINT_KEY.get(agent_choice), tablefmt="grid")
        print(" ")
        print(tabulate_tabulate)
        print(" ")
    if action == "delete":
        if len(args) > 0:
            _id = args[0]
        else:
            print("Delete takes one argument, the id")
            exit(1)
        agent.get_agent(agent_choice, project_id=project_id).delete(_id)
        print("Executed delete.")
    if action == "show":
        if len(args) > 0:
            _id = args[0]
        else:
            print("Show takes one argument, the id")
            exit(1)
        table = texttable.Texttable()
        table.set_cols_align(["l", "r"])
        table.set_cols_valign(["c", "b"])
        table.set_cols_dtype(['t', 't'])
        table.add_rows(
            get_result_to_show(agent.get_agent(agent_choice, project_id=project_id).find(_id[0]),
                               agent_choice))
        print(" ")
        print(table.draw() + "\n")
        # print(tabulate.tabulate(
        #     get_result_as_list_show(agent.get_agent(agent_choice, project_id=project_id).find(_id[0]), agent_choice),
        #     tablefmt="plain"))
        print(" ")
    if action == "create":
        if len(args[0]) > 0:
            params = args[0]
        else:
            print("create takes one argument, the object to create")
            exit(1)
        table = texttable.Texttable()
        table.set_cols_align(["l", "r"])
        table.set_cols_valign(["c", "b"])
        table.set_cols_dtype(['t', 't'])
        table.add_rows(
            get_result_to_show(agent.get_agent(agent_choice, project_id=project_id).create(params[0]),
                               agent_choice))
        print("\n")
        print(table.draw() + "\n\n")


def get_result_to_show(obj, agent_choice):
    if isinstance(obj, str) or type(obj) == unicode:
        obj = json.loads(obj)
    result = [["key", "value"]]
    for k, v in obj.iteritems():
        if k not in SHOW_EXCLUDE_KEY.get(agent_choice):
            if isinstance(v, list):
                if len(v) > 0:
                    tmp = []
                    if isinstance(v[0], dict):
                        tmp.append("ids:\n")
                        tmp.extend(["- " + x.get("id") for x in v])
                    # print("appending %s" % tmp)
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
    agent = MainAgent(nfvo_ip=nfvo_ip,
                      nfvo_port=nfvo_port,
                      https=https,
                      version=1,
                      username=username,
                      password=password,
                      project_id=project_id)

    # print(agent_choice, action, params)
    exec_action(agent, agent_choice, action, project_id, params)


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-pid", "--project-id", help="the project-id to use")
    parser.add_argument("-u", "--username", help="the openbaton username")
    parser.add_argument("-p", "--password", help="the openbaton password")
    parser.add_argument("-ip", "--nfvo-ip", help="the openbaton nfvo ip", default="localhost")
    parser.add_argument("--nfvo-port", help="the openbaton nfvo port", default="8080")

    parser.add_argument("agent", help="the agent you want to use. Possibilities are: \n" + str(SHOW_EXCLUDE_KEY.keys()))
    parser.add_argument("action", help="the action you want to call. Possibilities are: \n" + str(ACTIONS))
    parser.add_argument("params", help="The id, file or json", nargs='*')

    args = parser.parse_args()

    project_id = os.environ.get('OB_PROJECT_ID')
    username = os.environ.get('OB_USERNAME')
    password = os.environ.get('OB_PASSWORD')
    nfvo_ip = os.environ.get('OB_NFVO_IP')
    nfvo_port = os.environ.get('OB_NFVO_PORT')

    if args.username is not None:
        username = args.get("username")
    if args.password is not None:
        password = args.get("password")
    if args.nfvo_ip is not None:
        nfvo_ip = args.nfvo_ip
    if args.nfvo_port is not None:
        nfvo_port = args.nfvo_port
    if args.project_id is not None:
        project_id = args.project_id

    if project_id is None:
        project_id = raw_input("insert project-id: ")
    if username is None or username == "":
        username = raw_input("insert user: ")
    if nfvo_ip is None or nfvo_ip == "":
        nfvo_ip = raw_input("insert nfvo_ip: ")
    if nfvo_port is None or nfvo_port == "":
        nfvo_port = raw_input("insert nfvo_port: ")
    if password is None or password == "":
        password = getpass.getpass("insert password: ")

    # print('')
    # print("username '%s'" % username)
    # print("password '%s'" % password)
    # print("project_id '%s'" % project_id)
    # print("nfvo_ip '%s'" % nfvo_ip)
    # print("nfvo_port '%s'" % nfvo_port)

    openbaton(args.agent, args.action, params=args.params, project_id=project_id, username=username, password=password,
              nfvo_ip=nfvo_ip, nfvo_port=nfvo_port)


if __name__ == '__main__':
    print("Open Baton fancy CLI :)")
