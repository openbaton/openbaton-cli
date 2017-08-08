import json
import logging

from org.openbaton.cli.agents.agents import OpenBatonAgentFactory
from org.openbaton.cli.errors.errors import NfvoException
from org.openbaton.sdk.utils import get_config, get_config_file_location


class OBClient(object):
    def __init__(self, nfvo_ip=None, nfvo_port=None, username=None, password=None, https=False, project_name=None,
                 version=1):
        """
        If username, password, ip, port etc are passed, it will create a openbaton agent using these ones. if not it
        will use the        configuration parameter ones.

        :param nfvo_ip: the NFVO ip
        :param nfvo_port: the NFVO port
        :param username: the NFVO username
        :param password: the NFVO password
        :param https: if https is enabled
        :param project_name: the name of the project, can be None
        :param version: 1 for now...
        """

        self.https = https or get_config("nfvo", "https", get_config_file_location()).lower() == 'true'
        self.username = username or get_config("nfvo", "username", get_config_file_location())
        self.password = password or get_config("nfvo", "password", get_config_file_location())
        self.nfvo_ip = nfvo_ip or get_config("nfvo", "ip", get_config_file_location())
        self.nfvo_port = nfvo_port or get_config("nfvo", "port", get_config_file_location())

        self.agent_factory = OpenBatonAgentFactory(nfvo_ip=self.nfvo_ip,
                                                   nfvo_port=self.nfvo_port,
                                                   https=self.https,
                                                   version=self.version,
                                                   username=self.username,
                                                   password=self.password,
                                                   project_id=None)
        if project_name:
            self.project_id = self._get_project_id(project_name)

    def _get_project_id(self, project_name):
        project_agent = self.agent_factory.get_project_agent()
        for project in json.loads(project_agent.find()):
            if project.get('name') == project_name:
                return project.get('id')
        return None

    def list_nsds(self):
        return json.loads(self.agent_factory.get_ns_descriptor_agent(self.project_id).find())

    def create_nsr(self, nsd_id, body=None):
        return self.agent_factory.get_ns_records_agent(self.project_id).create(nsd_id, body)

    def delete_nsr(self, nsr_id):
        return self.agent_factory.get_ns_records_agent(self.project_id).delete(nsr_id)

    def create_project(self, project):
        for p in json.loads(self.list_projects()):
            if p.get('name') == project.get('name'):
                return p
        if isinstance(project, dict):
            project = json.dumps(project)
        ob_project = self.agent_factory.get_project_agent().create(project)
        self.project_id = ob_project.get('id')
        return ob_project

    def create_user(self, user):

        for us in json.loads(self.list_users()):
            if us.get('username') == user.get('username'):
                return us

        if isinstance(user, dict):
            user = json.dumps(user)
        return self.agent_factory.get_user_agent(self.project_id).create(user)

    def create_vim_instance(self, vim_instance):
        for vi in self.list_vim_instances():
            if vi.get('name') == vim_instance.get('name'):
                return vi
        if isinstance(vim_instance, dict):
            vim_instance = json.dumps(vim_instance)

        logging.debug("Posting vim %s" % vim_instance)
        return self.agent_factory.get_vim_instance_agent(self.project_id).create(vim_instance)

    def list_users(self):
        return self.agent_factory.get_user_agent(self.project_id).find()

    def list_projects(self):
        return self.agent_factory.get_project_agent().find()

    def list_vim_instances(self):
        return json.loads(self.agent_factory.get_vim_instance_agent(self.project_id).find())

    def upload_package(self, package_path, name=None):
        package_agent = self.agent_factory.get_vnf_package_agent(self.project_id)
        try:
            return package_agent.create(package_path)
        except NfvoException as e:
            if not name:
                raise e
            for nsd in json.loads(self.agent_factory.get_ns_descriptor_agent(self.project_id).find()):
                for vnfd in nsd.get('vnfd'):
                    if vnfd.get('name') == name:
                        return {"id": vnfd.get('id')}
            raise e

    def create_nsd(self, nsd):
        if isinstance(nsd, dict):
            nsd = json.dumps(nsd)
        return self.agent_factory.get_ns_descriptor_agent(self.project_id).create(nsd)

    def get_nsd(self, nsd_id):
        return self.agent_factory.get_ns_descriptor_agent(self.project_id).find(nsd_id)

    def delete_nsd(self, nsd_id):
        self.agent_factory.get_ns_descriptor_agent(self.project_id).delete(nsd_id)

    def delete_vnfd(self, vnfd_id):
        self.agent_factory.get_vnf_descriptor_agent(self.project_id).delete(vnfd_id)

    def get_nsr(self, nsr_id):
        return self.agent_factory.get_ns_records_agent(self.project_id).find(nsr_id)

    def import_key(self, ssh_pub_key, name):

        key_agent = self.agent_factory.get_key_agent(self.project_id)
        for key in json.loads(key_agent.find()):
            if key.get('name') == name:
                key_agent.delete(key.get('id'))
                break

        key_agent.create(
            json.dumps(
                {
                    'name': name,
                    'projectId': self.project_id,
                    'publicKey': ssh_pub_key
                }
            )
        )

    def create_nsd_from_csar(self, location):
        return self.agent_factory.get_csarnsd_agent(self.project_id).create(location)

    def delete_user(self, username):
        for u in json.loads(self.list_users()):
            if u.get('username') == username:
                self.agent_factory.get_user_agent(self.project_id).delete(u.get('id'))

    def delete_project(self, ob_project_id):
        self.agent_factory.get_project_agent().delete(ob_project_id)

    def list_nsrs(self):
        return json.loads(self.agent_factory.get_ns_records_agent(self.project_id).find())

    def delete_vim_instance(self, _vim_id):
        self.agent_factory.get_vim_instance_agent(self.project_id).delete(_vim_id)
