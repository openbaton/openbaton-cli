from __future__ import print_function
import json
import os
from org.openbaton.cli.errors.errors import WrongParameters
from org.openbaton.cli.utils.RestClient import RestClient


class BaseAgent(object):
    def __init__(self, client, url, project_id=None):
        self._client = client
        self.url = url
        if project_id is not None:
            self._client.project_id = project_id

    def find(self, _id=""):
        return self._client.get(self.url + "/%s" % _id)

    def delete(self, _id):
        self._client.delete(self.url + "/%s" % _id)

    def update(self, _id, entity):
        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            return json.loads(self._client.put(self.url + "/%s" % _id, json.dumps(json.loads(entity))))
        else:
            with open(entity) as f:
                return json.loads(self._client.put(self.url + "/%s" % _id, json.dumps(f.read().replace('\n', ''))))

    def create(self, entity, _id=""):
        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            result = json.loads(self._client.post(self.url + "/%s" % _id, json.dumps(json.loads(entity))))
            return result
        else:
            if not os.path.isfile(entity):
                raise WrongParameters("%s is not a file")
            with open(entity) as f:
                return json.loads(self._client.post(self.url + "/%s" % _id, json.dumps(f.read().replace('\n', ''))))


class ProjectAgent(BaseAgent):
    def __init__(self, client):
        super(ProjectAgent, self).__init__(client, "projects")


class VimInstanceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VimInstanceAgent, self).__init__(client, "datacenters", project_id=project_id)


class NSRAgent(BaseAgent):
    def create(self, entity, _id="{}"):
        entity = entity.strip()
        return json.loads(self._client.post(self.url + "/%s" % entity, json.dumps(json.loads(_id))))

    def __init__(self, client, project_id):
        super(NSRAgent, self).__init__(client, "ns-records", project_id=project_id)


class NSDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(NSDAgent, self).__init__(client, "ns-descriptors", project_id=project_id)


class VNFPackageAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFPackageAgent, self).__init__(client, "vnf-packages", project_id=project_id)

    def create(self, entity, _id=""):
        if os.path.exists(entity) and os.path.isfile(entity) and entity.endswith(".tar"):
            return json.loads(self._client.post_file(self.url + "/%s" % _id, open(entity, "r")))


class SubAgent(BaseAgent):
    def __init__(self, client, project_id, main_agent_url, main_agent, sub_url, sub_obj):
        super(SubAgent, self).__init__(client, main_agent_url, project_id=project_id)
        self.sub_obj = sub_obj
        self._main_agent = main_agent
        self.sub_url = sub_url

    def update(self, _id, entity):
        nsd_id = self._get_sub_obj_id_from_id(_id)
        return super(SubAgent, self).update(nsd_id + "/" + self.sub_url + "/" + _id, entity)

    def find(self, _id=""):
        if _id is None or _id == "":
            raise WrongParameters("Please provide the id, only action show is allowed on this agent")
        nsd_id = self._get_sub_obj_id_from_id(_id)
        return super(SubAgent, self).find(nsd_id + "/" + self.sub_url + "/" + _id)

    def delete(self, _id):
        nsd_id = self._get_sub_obj_id_from_id(_id)
        super(SubAgent, self).delete(nsd_id + "/" + self.sub_url + "/" + _id)

    def create(self, entity, _id=""):
        if _id is None or _id == "":
            raise WrongParameters("Please provide the id  of the object where to create this entity")
        return super(SubAgent, self).create(entity, _id + "/" + self.sub_url + "/")

    def _get_sub_obj_id_from_id(self, _id):
        for obj in json.loads(self._main_agent.find()):
            for sub_obj in obj.get(self.sub_obj):
                if sub_obj.get("id") == _id:
                    return obj.get("id")


class VNFDAgent(SubAgent):
    def __init__(self, client, project_id):
        super(VNFDAgent, self).__init__(client,
                                        project_id,
                                        "ns-descriptors",
                                        NSDAgent(client, project_id),
                                        "vnfdescriptors",
                                        "vnfd")


class VNFRAgent(SubAgent):
    def __init__(self, client, project_id):
        super(VNFRAgent, self).__init__(client,
                                        project_id,
                                        "ns-records",
                                        NSRAgent(client, project_id),
                                        "vnfrecords",
                                        "vnfr")


class MainAgent(object):
    def __init__(self, nfvo_ip="localhost", nfvo_port="8080", https=False, version=1, username=None, password=None,
                 project_id=None):
        # print
        # print username
        # print
        self.nfvo_ip = nfvo_ip
        self.nfvo_port = nfvo_port
        self.https = https
        self.version = version
        self.username = username

        self.password = password
        self._client = RestClient(nfvo_ip=self.nfvo_ip,
                                  nfvo_port=self.nfvo_port,
                                  https=self.https,
                                  version=self.version,
                                  username=self.username,
                                  password=self.password,
                                  project_id=project_id)

        self._project_agent = None
        self._vim_instance_agent = None
        self._ns_records_agent = None
        self._ns_descriptor_agent = None
        self._vnf_package_agent = None
        self._vnf_descriptor_agent = None
        self._vnf_record_agent = None

    def get_project_agent(self):
        if self._project_agent is None:
            self._project_agent = ProjectAgent(self._client)
        return self._project_agent

    def get_vim_instance_agent(self, project_id):
        if self._vim_instance_agent is None:
            self._vim_instance_agent = VimInstanceAgent(self._client, project_id=project_id)
        self._vim_instance_agent.project_id = project_id
        return self._vim_instance_agent

    def get_ns_records_agent(self, project_id):
        if self._ns_records_agent is None:
            self._ns_records_agent = NSRAgent(self._client, project_id=project_id)
        self._ns_records_agent.project_id = project_id
        return self._ns_records_agent

    def get_ns_descriptor_agent(self, project_id):
        if self._ns_descriptor_agent is None:
            self._ns_descriptor_agent = NSDAgent(self._client, project_id=project_id)
        self._ns_descriptor_agent.project_id = project_id
        return self._ns_descriptor_agent

    def get_vnfd_descriptor_agent(self, project_id):
        if self._vnf_descriptor_agent is None:
            self._vnf_descriptor_agent = VNFDAgent(self._client, project_id=project_id)
        self._vnf_descriptor_agent.project_id = project_id
        return self._vnf_descriptor_agent

    def get_vnfr_descriptor_agent(self, project_id):
        if self._vnf_record_agent is None:
            self._vnf_record_agent = VNFRAgent(self._client, project_id=project_id)
        self._vnf_record_agent.project_id = project_id
        return self._vnf_record_agent

    def get_vnf_package_agent(self, project_id):
        if self._vnf_package_agent is None:
            self._vnf_package_agent = VNFPackageAgent(self._client, project_id=project_id)
        self._vnf_package_agent.project_id = project_id
        return self._vnf_package_agent

    def get_agent(self, agent, project_id):
        if agent == "nsr":
            return self.get_ns_records_agent(project_id)
        if agent == "nsd":
            return self.get_ns_descriptor_agent(project_id)
        if agent == "vnfd":
            return self.get_vnfd_descriptor_agent(project_id)
        if agent == "vnfr":
            return self.get_vnfr_descriptor_agent(project_id)
        if agent == "vim":
            return self.get_vim_instance_agent(project_id)
        if agent == "vnfpackage":
            return self.get_vnf_package_agent(project_id)
        if agent == "project":
            return self.get_project_agent()
