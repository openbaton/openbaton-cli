import abc
import six
import os
import sys
import traceback

import cliff
from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager

from org.openbaton.config import PRINT_FORMATS, ACTIONS
from org.openbaton.sdk.client import OBClient
from org.openbaton.v2.errors import WrongActionError


@six.add_metaclass(abc.ABCMeta)
class BaseObCmd(Command):
    parser = None

    @abc.abstractmethod
    def list(self):
        pass

    @abc.abstractmethod
    def create(self, params):
        pass

    @abc.abstractmethod
    def find(self, params):
        pass

    @abc.abstractmethod
    def delete(self, params):
        pass

    def help(self):
        self.parser.print_help()

    def get_parser(self, prog_name):
        parser = super(BaseObCmd, self).get_parser(prog_name)
        parser.add_argument("action",
                            metavar="<action>",
                            help="the action you want to call. Possibilities are: \n" + str(ACTIONS),
                            nargs='?',
                            default='list')
        parser.add_argument("params",
                            metavar="<parameter>",
                            help="The id, file or json",
                            nargs='*')
        self.parser = parser
        return parser

    def handle_special_action(self, action, params):
        raise WrongActionError("Action '%s' not known" % action)

    def take_action(self, parsed_args):
        action = parsed_args.action
        params = parsed_args.params
        res = None
        if action == 'list':
            res = self.list()
        elif action == 'create':
            res = self.create(params)
        elif action == 'show':
            res = self.find(params)
        elif action == 'help':
            self.help()
        elif action == 'delete' or action == 'remove':
            res = self.delete(params)
        else:
            res = self.handle_special_action(action, params)
        if res:
            self.app.stdout.write("%s\n" % res)
            return


class OpenBatonCmd(App):
    intro = 'Open Baton shell, have fun \n'
    project_id = ''
    project_name = 'default'
    username = 'admin'
    password = 'openbaton'
    nfvo_ip = 'localhost'
    nfvo_port = 8080
    nfvo_ssl = False
    ob_client = None
    format = ''

    def __init__(self):
        super(OpenBatonCmd, self).__init__(
            description='openbaton demo app',
            version='0.1',
            command_manager=CommandManager('openbaton.cmd'),
            deferred_help=True,
        )
        self.command_manager.add_command('complete', cliff.complete.CompleteCommand)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(OpenBatonCmd, self).build_option_parser(description, version, argparse_kwargs)

        parser.add_argument("-u", "--username",
                            metavar="<username>",
                            default=os.environ.get('OB_USERNAME'),
                            help="the openbaton username")
        parser.add_argument("-p", "--password",
                            metavar="<password>",
                            default=os.environ.get('OB_PASSWORD'),
                            help="the openbaton password")
        parser.add_argument("-ip", "--nfvo-ip",
                            metavar="<nfvo-ip>",
                            default=os.environ.get('OB_NFVO_IP'),
                            help="the openbaton nfvo ip")
        parser.add_argument("--nfvo-port",
                            metavar="<nfvo-port>",
                            default=os.environ.get('OB_NFVO_PORT'),
                            help="the openbaton nfvo port")

        project_group = parser.add_mutually_exclusive_group()
        project_group.add_argument("--project-id",
                                   metavar="<project-id>",
                                   default=os.environ.get('OB_PROJECT_ID'),
                                   help="the project-id to use")
        project_group.add_argument("--project-name",
                                   metavar="<project-name>",
                                   default=os.environ.get('OB_PROJECT_NAME'),
                                   help="the project-name to use")
        parser.add_argument("--ssl",
                            default=os.environ.get('OB_NFVO_SSL') in [True, "true", "True", "TRUE"],
                            help="use HTTPS instead of HTTP", action="store_true")
        parser.add_argument("--format",
                            default="table",
                            help="json or table",
                            choices=PRINT_FORMATS)
        return parser

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app %s', argv)
        self.ob_client = self.get_ob_client()

    def get_ob_client(self):
        if self.options.username:
            self.username = self.options.username
        if self.options.password:
            self.password = self.options.password
        if self.options.nfvo_ip:
            self.nfvo_ip = self.options.nfvo_ip
        if self.options.nfvo_port:
            self.nfvo_port = self.options.nfvo_port
        if self.options.project_id:
            self.project_id = self.options.project_id
        if self.options.ssl is not None:
            self.nfvo_ssl = self.options.ssl
        self.format = self.options.format

        return OBClient(nfvo_ip=self.nfvo_ip,
                        nfvo_port=self.nfvo_port,
                        username=self.username,
                        password=self.password,
                        https=self.nfvo_ssl,
                        project_name=self.project_name)

    def clean_up(self, cmd, result, err):
        if err:
            if self.options.debug:
                traceback.print_exc()


def start_single_command():
    ob_cmd = OpenBatonCmd()

    # parser = argparse.ArgumentParser()

    return ob_cmd.run(sys.argv[1:])
