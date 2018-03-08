import json
import logging

from org.openbaton.cli.agents.agents import OpenBatonAgentFactory
from org.openbaton.cli.errors.errors import NfvoException


class OBClient(object):
    def __init__(self, nfvo_ip=None, nfvo_port=None, username=None, password=None, https=False, project_name=None,
                 project_id=None,
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

        self.https = https
        self.username = username
        self.password = password
        self.nfvo_ip = nfvo_ip
        self.nfvo_port = nfvo_port
        self.version = version
        self.project_id = None
        self.agent_factory = OpenBatonAgentFactory(nfvo_ip=self.nfvo_ip,
                                                   nfvo_port=self.nfvo_port,
                                                   https=self.https,
                                                   version=self.version,
                                                   username=self.username,
                                                   password=self.password,
                                                   project_id=project_id)
        if not project_id and project_name:
            self.project_id = self._get_project_id(project_name)

    # UTILITIES
    def _get_project_id(self, project_name):
        project_agent = self.agent_factory.get_project_agent()
        for project in json.loads(project_agent.find()):
            if project.get('name') == project_name:
                return project.get('id')
        return None

    ####################
    ####### LIST #######
    ####################

    def list_users(self):
        return json.loads(self.agent_factory.get_user_agent(self.project_id).find())

    def list_keys(self):
        return json.loads(self.agent_factory.get_key_agent(self.project_id).find())

    def list_event(self):
        return json.loads(self.agent_factory.get_event_agent(self.project_id).find())

    def list_services(self):
        return json.loads(self.agent_factory.get_service_agent(self.project_id).find())

    def list_projects(self):
        return json.loads(self.agent_factory.get_project_agent().find())

    def list_packages(self):
        return json.loads(self.agent_factory.get_vnf_package_agent(self.project_id).find())

    def list_vims(self):
        return json.loads(self.agent_factory.get_vim_instance_agent(self.project_id).find())

    def list_nsds(self):
        return json.loads(self.agent_factory.get_ns_descriptor_agent(self.project_id).find())

    def list_nsrs(self):
        return json.loads(self.agent_factory.get_ns_records_agent(self.project_id).find())

    ####################
    ###### CREATE ######
    ####################

    def create_nsr(self, nsd_id, body=None):
        return self.agent_factory.get_ns_records_agent(self.project_id).create(nsd_id, body)

    def create_project(self, project):
        for p in json.loads(self.list_projects()):
            if p.get('name') == project.get('name'):
                return p
        if isinstance(project, dict):
            project = json.dumps(project)
        ob_project = self.agent_factory.get_project_agent().create(project)
        self.project_id = ob_project.get('id')
        return ob_project

    def create_event(self, event):
        for e in self.list_event():
            if e.get('name') == e.get('name'):
                return e
        if isinstance(event, dict):
            event = json.dumps(event)
        ob_event = self.agent_factory.get_event_agent(self.project_id).create(event)
        return ob_event

    def create_user(self, user):

        for us in json.loads(self.list_users()):
            if us.get('username') == user.get('username'):
                return us

        if isinstance(user, dict):
            user = json.dumps(user)
        return json.loads(self.agent_factory.get_user_agent(self.project_id).create(user))

    def create_service(self, service):

        for srv in self.list_services():
            if srv.get('name') == service.get('name'):
                return srv

        if isinstance(service, dict):
            service = json.dumps(service)
        return self.agent_factory.get_service_agent(self.project_id).create(service)

    def create_vim_instance(self, vim_instance):
        for vi in self.list_vims():
            if vi.get('name') == vim_instance.get('name'):
                return vi
        if isinstance(vim_instance, dict):
            vim_instance = json.dumps(vim_instance)

        logging.debug("Posting vim %s" % vim_instance)
        return self.agent_factory.get_vim_instance_agent(self.project_id).create(vim_instance)

    def create_package(self, package_path, name=None):
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

    def create_key(self, key_nme):
        return self.agent_factory.get_key_agent(self.project_id).create(key_nme)

    def import_key(self, name, ssh_pub_key):
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

    def create_nsd_from_market(self, link):
        return self.agent_factory.get_market_agent(self.project_id).create(link)

    def refresh_vim(self, vim_id):
        return json.loads(self.agent_factory.get_vim_instance_agent(self.project_id).refresh(vim_id))

    ####################
    ###### DELETE ######
    ####################

    def delete_nsr(self, nsr_id):
        return self.agent_factory.get_ns_records_agent(self.project_id).delete(nsr_id)

    def delete_nsd(self, nsd_id):
        self.agent_factory.get_ns_descriptor_agent(self.project_id).delete(nsd_id)

    def delete_key(self, key_id):
        self.agent_factory.get_key_agent(self.project_id).delete(key_id)

    def delete_vnfd(self, vnfd_id):
        self.agent_factory.get_vnf_descriptor_agent(self.project_id).delete(vnfd_id)

    def delete_user(self, username):
        for u in json.loads(self.list_users()):
            if u.get('username') == username:
                self.agent_factory.get_user_agent(self.project_id).delete(u.get('id'))

    def delete_project(self, ob_project_id):
        self.agent_factory.get_project_agent().delete(ob_project_id)

    def delete_service(self, service_id):
        self.agent_factory.get_service_agent(self.project_id).delete(service_id)

    def delete_event(self, ob_event_id):
        self.agent_factory.get_event_agent(self.project_id).delete(ob_event_id)

    def delete_vim_instance(self, _vim_id):
        self.agent_factory.get_vim_instance_agent(self.project_id).delete(_vim_id)

    def delete_package(self, package_id):
        self.agent_factory.get_vnf_package_agent(self.project_id).delete(package_id)

    ####################
    ####### SHOW #######
    ####################

    def get_nsd(self, nsd_id):
        return self.agent_factory.get_ns_descriptor_agent(self.project_id).find(nsd_id)

    def get_key(self, key_id):
        return self.agent_factory.get_key_agent(self.project_id).find(key_id)

    def get_package(self, package_id):
        return json.loads(self.agent_factory.get_vnf_package_agent(self.project_id).find(package_id))

    def get_nsr(self, nsr_id):
        return self.agent_factory.get_ns_records_agent(self.project_id).find(nsr_id)

    def get_vim(self, vim_id):
        return json.loads(self.agent_factory.get_vim_instance_agent(self.project_id).find(vim_id))

    def get_script(self, script_id):
        return json.loads(self.agent_factory.get_script_agent(self.project_id).find(script_id))

    def get_service(self, service_id):
        return self.agent_factory.get_service_agent(self.project_id).find(service_id)

    def get_user(self, user_id):
        return self.agent_factory.get_user_agent(self.project_id).find(user_id)
