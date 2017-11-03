from __future__ import print_function

import json
import os

from org.openbaton.cli.errors.errors import WrongParameters, NotFoundException, SdkException
from org.openbaton.cli.utils.RestClient import RestClient


def _get_parents_obj_id_from_id(id_to_find, main_agent, first_level, second_level=None, third_level=None):
    for obj in json.loads(main_agent.find()):
        for sub_obj in obj.get(first_level):
            if not second_level:
                if sub_obj.get("id") == id_to_find:
                    return obj.get('id'), sub_obj
            else:
                for sub_sub_obj in sub_obj.get(second_level):
                    if not third_level:
                        if sub_sub_obj.get("id") == id_to_find:
                            return obj.get("id"), sub_obj.get('id'), sub_sub_obj
                    else:
                        for sub_sub_sub_obj in sub_sub_obj.get(third_level):
                            if sub_sub_sub_obj.get("id") == id_to_find:
                                return obj.get("id"), sub_obj.get('id'), sub_sub_obj.get('id'), sub_sub_sub_obj
    # if no parent object was found, we can safely assume that the child object does not exist
    raise NotFoundException('No {} found with ID {}'.format(first_level, id_to_find))


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
            try:
                entity_json = json.loads(entity)
            except:
                raise SdkException('The passed JSON seems to be invalid.')
            return json.loads(self._client.put(self.url + "/%s" % _id, json.dumps(entity_json)))
        else:
            if not os.path.isfile(entity):
                raise WrongParameters("{} is not a file".format(entity))
            with open(entity) as f:
                try:
                    entity_json = f.read().replace('\n', '')
                except:
                    raise SdkException('The passed JSON seems to be invalid.')
                return json.loads(self._client.put(self.url + "/%s" % _id, json.dumps(entity_json)))

    def create(self, entity='{}', _id=""):
        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            try:
                entity_json = json.loads(entity)
            except:
                raise SdkException('The passed JSON seems to be invalid.')
            result = json.loads(self._client.post(self.url + "/%s" % _id, json.dumps(entity_json)))
            return result
        else:
            if not os.path.isfile(entity):
                raise WrongParameters("{} is not a file".format(entity))
            with open(entity) as f:
                file_content = f.read().replace('\n', '')
                try:
                    entity_json = json.loads(file_content)
                except:
                    raise SdkException('The passed JSON seems to be invalid.')
                return json.loads(self._client.post(self.url + "/%s" % _id, json.dumps(entity_json)))


class ProjectAgent(BaseAgent):
    def __init__(self, client):
        super(ProjectAgent, self).__init__(client, "projects")


class EventAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(EventAgent, self).__init__(client, "events", project_id=project_id)


class VimInstanceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VimInstanceAgent, self).__init__(client, "datacenters", project_id=project_id)

    def refresh(self, _id):
        self._client.get(self.url + "/%s/refresh" % _id)


class NSRAgent(BaseAgent):
    def create(self, entity='', _id="{}"):
        entity = entity.strip()
        return json.loads(self._client.post(self.url + "/%s" % entity, json.dumps(json.loads(_id))))

    def __init__(self, client, project_id):
        super(NSRAgent, self).__init__(client, "ns-records", project_id=project_id)

        # {id}/vnfrecords/{idVnf}/vdunits/vnfcinstances


class VNFCInstanceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFCInstanceAgent, self).__init__(client, "ns-records", project_id=project_id)

    # {id}/vnfrecords/{idVnf}/vdunits/vnfcinstances
    def delete(self, nsr_id, vnfr_id, vdu_id="", vnfci_id=""):
        return self._client.delete(
            "%s/%s/vnfrecords/%s/vdunits/%s/vnfcinstances/%s" % (self.url, nsr_id, vnfr_id, vdu_id, vnfci_id))

    def create(self, entity, nsr_id, vnfr_id, vdu_id="", standby=False, ):
        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            try:
                entity_dict = json.loads(entity)
            except:
                raise SdkException('The passed JSON seems to be invalid.')
        else:
            if not os.path.isfile(entity):
                raise WrongParameters("{} is neither a file nor does it seem to be valid JSON".format(entity))
            with open(entity) as f:
                file_content = f.read().replace('\n', '')
                try:
                    entity_dict = json.loads(file_content)
                except:
                    raise SdkException('The passed JSON seems to be invalid.')

        if standby:
            if (vdu_id is None or vdu_id == ''):
                raise WrongParameters('When creating standby VNFCInstances you have to specify the VDU.')
            return self._client.post(
                "{}/{}/vnfrecords/{}/vdunits/{}/vnfcinstances/standby".format(self.url, nsr_id, vnfr_id, vdu_id),
                json.dumps(entity_dict))
        else:
            return self._client.post(
                "{}/{}/vnfrecords/{}/vdunits/{}/vnfcinstances".format(self.url, nsr_id, vnfr_id, vdu_id),
                json.dumps(entity_dict))

    def update(self, _id, entity):
        raise WrongParameters('VNFC Instance agent is allowed only to execute "create" and "delete"')

    def find(self, _id=""):
        if not _id:
            raise WrongParameters("Please provide the id")
        nsr_id, vnfr_id, vdu_id, vnfci = _get_parents_obj_id_from_id(_id,
                                                                     NSRAgent(self._client, self._client.project_id),
                                                                     'vnfr', 'vdu', 'vnfc_instance')
        return vnfci


class KeyAgent(BaseAgent):
    def create(self, entity='', _id=None):
        if os.path.exists(entity) and os.path.isfile(entity):  # import
            with open(entity, 'r') as f:
                entity = f.read().replace('\n', '')

        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            try:
                entity_json = json.loads(entity)
            except:
                raise SdkException('The passed JSON seems to be invalid.')
            result = json.loads(self._client.post(self.url, json.dumps(entity_json)))
            return result
        else:  # generate
            key = self._client.post("%s/%s" % (self.url, 'generate'), entity)
        return key

    def __init__(self, client, project_id):
        super(KeyAgent, self).__init__(client, "keys", project_id=project_id)


class UserAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(UserAgent, self).__init__(client, "users", project_id=project_id)


class ServiceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(ServiceAgent, self).__init__(client, "components/services", project_id=project_id)

    def create(self, entity='{}', _id=""):
        headers = {"content-type": "application/json", "accept": "application/octet-stream"}

        entity = entity.strip()
        if entity.endswith("}") or entity.endswith("]"):
            try:
                entity_json = json.loads(entity)
            except:
                raise SdkException('The passed JSON seems to be invalid.')
            return self._client.post(self.url + "/create/%s" % _id, json.dumps(entity_json), headers=headers)
        else:
            if not os.path.isfile(entity):
                raise WrongParameters("%s is not a file")
            with open(entity) as f:
                file_content = f.read().replace('\n', '')
                try:
                    entity_json = json.loads(file_content)
                except:
                    raise SdkException('The passed JSON seems to be invalid.')
                return self._client.post(self.url + "/create/%s" % _id, body=json.dumps(entity_json),
                                         headers=headers)


class MarketAgent(BaseAgent):
    def update(self, _id, entity):
        raise WrongParameters('Market agent is allowed only to execute "create" passing a link')

    def delete(self, _id):
        raise WrongParameters('Market agent is allowed only to execute "create" passing a link')

    def find(self, _id=""):
        raise WrongParameters('Market agent is allowed only to execute "create" passing a link')

    def create(self, entity, _id="{}"):
        # entity will be the link
        entity = entity.strip()
        entity = {
            "link": entity
        }
        return json.loads(self._client.post(self.url, json.dumps(entity)))

    def __init__(self, client, project_id):
        super(MarketAgent, self).__init__(client, "ns-descriptors/marketdownload", project_id=project_id)


class LogAgent(BaseAgent):
    def update(self, _id, entity):
        raise WrongParameters('The log agent is only allowed to execute "show" passing: nsr_id, vnfr_name, hostname')

    def delete(self, _id):
        raise WrongParameters('The log agent is only allowed to execute "show" passing: nsr_id, vnfr_name, hostname')

    def find(self, nsr_id=None, vnfr_name=None, hostname=None, lines=None):
        if not vnfr_name or not hostname or not nsr_id:
            raise WrongParameters(
                'The log agent is only allowed to execute "show" passing: nsr_id, vnfr_name and hostname')
        if lines:
            body = json.dumps({'lines': int(lines)})
        else:
            body = None
        return self._client.post(self.url + "/%s/vnfrecord/%s/hostname/%s" % (nsr_id, vnfr_name, hostname), body)

    def create(self, entity, _id="{}"):
        raise WrongParameters('The log agent is only allowed to execute "show" passing: nsr_id, vnfr_name, hostname')

    def __init__(self, client, project_id):
        super(LogAgent, self).__init__(client, "logs", project_id=project_id)


class NSDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(NSDAgent, self).__init__(client, "ns-descriptors", project_id=project_id)


class VNFPackageAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFPackageAgent, self).__init__(client, "vnf-packages", project_id=project_id)

    def create(self, entity='', _id=""):
        if os.path.exists(entity) and os.path.isfile(entity) and entity.endswith(".tar"):
            return json.loads(self._client.post_file(self.url + "/%s" % _id, open(entity, "rb")))


class CSARNSDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(CSARNSDAgent, self).__init__(client, "csar-nsd", project_id=project_id)

    def create(self, entity='', _id=""):
        if os.path.exists(entity) and os.path.isfile(entity) and entity.endswith(".csar"):
            return json.loads(self._client.post_file(self.url + "/%s" % _id, open(entity, "rb")))
        else:  # it is not a .csar file but a marketplace link
            return json.loads(self._client.post(self.url[:-1] + "/marketdownload/%s" % _id, '{"link":"%s"}' % entity))

    def update(self, _id, entity):
        raise WrongParameters('csarnsd agent is only allowed to execute "create"')

    def delete(self, _id):
        raise WrongParameters('csarnsd agent is only allowed to execute "create"')

    def find(self, _id=""):
        raise WrongParameters('csarnsd agent is only allowed to execute "create"')


class CSARVNFDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(CSARVNFDAgent, self).__init__(client, "csar-vnfd", project_id=project_id)

    def create(self, entity='', _id=""):
        if os.path.exists(entity) and os.path.isfile(entity) and entity.endswith(".csar"):
            return json.loads(self._client.post_file(self.url + "/%s" % _id, open(entity, "rb")))
        else:  # it is not a .csar file but a marketplace link
            return json.loads(self._client.post(self.url[:-1] + "/marketdownload/%s" % _id, '{"link":"%s"}' % entity))

    def update(self, _id, entity):
        raise WrongParameters('csarvnfd agent is only allowed to execute "create"')

    def delete(self, _id):
        raise WrongParameters('Market agent is only allowed to execute "create"')

    def find(self, _id=""):
        raise WrongParameters('Market agent is only allowed to execute "create"')


class VNFDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFDAgent, self).__init__(client=client, url="vnf-descriptors", project_id=project_id)


class SubAgent(BaseAgent):
    def __init__(self, client, project_id, main_agent, sub_url, sub_obj):
        super(SubAgent, self).__init__(client, main_agent.url, project_id=project_id)
        self.sub_obj = sub_obj
        self.sub_url = sub_url
        self._main_agent = main_agent

    def update(self, _id, entity):
        parent_obj_id, _ = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj)
        return super(SubAgent, self).update(parent_obj_id + "/" + self.sub_url + "/" + _id, entity)

    def find(self, _id=""):
        if not _id:
            raise WrongParameters(
                "Please provide the ID. The 'show' action is allowed on this agent but not the 'list' action.")
        parent_obj_id, obj = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj)
        return json.dumps(obj)

    def delete(self, _id):
        parent_obj_id, _ = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj)
        super(SubAgent, self).delete(parent_obj_id + "/" + self.sub_url + "/" + _id)

    def create(self, entity='', _id=""):
        if _id is None or _id == "":
            raise WrongParameters("Please provide the id of the object where to create this entity")
        return super(SubAgent, self).create(entity, _id + "/" + self.sub_url + "/")


class VNFRAgent(SubAgent):
    def __init__(self, client, project_id, main_agent):
        super(VNFRAgent, self).__init__(client=client,
                                        project_id=project_id,
                                        main_agent=main_agent,
                                        sub_url='vnfrecords',
                                        sub_obj="vnfr")


class VDUAgent(SubAgent):
    def __init__(self, client, project_id, main_agent):
        super(VDUAgent, self).__init__(client=client,
                                       project_id=project_id,
                                       main_agent=main_agent,
                                       sub_url='vnfrecords',
                                       sub_obj="vnfr")

    def find(self, _id=""):
        if _id is None or _id == "":
            raise WrongParameters("Please provide the id, only action show is allowed on this agent")
        nsr_id, vnfr_id, vdu = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj, 'vdu')
        return vdu


class OpenBatonAgentFactory(object):
    def __init__(self, nfvo_ip="localhost", nfvo_port="8080", https=False, version=1, username=None, password=None,
                 project_id=None):

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
        self._event_agent = None
        self._vim_instance_agent = None
        self._ns_records_agent = None
        self._ns_descriptor_agent = None
        self._vnf_package_agent = None
        self._vnf_descriptor_agent = None
        self._vnf_record_agent = None
        self._market_agent = None
        self._user_agent = None
        self._csarnsd_agent = None
        self._csarvnfd_agent = None
        self._key_agent = None
        self._log_agent = None
        self._vnfci_agent = None
        self._vdu_agent = None
        self._service_agent = None

    def get_project_agent(self):
        if self._project_agent is None:
            self._project_agent = ProjectAgent(self._client)
        return self._project_agent

    def get_event_agent(self, project_id):
        if self._event_agent is None:
            self._event_agent = EventAgent(self._client, project_id=project_id)
        self._event_agent.project_id = project_id
        return self._event_agent

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

    def get_vnf_descriptor_agent(self, project_id):
        if self._vnf_descriptor_agent is None:
            self._vnf_descriptor_agent = VNFDAgent(client=self._client, project_id=project_id)
        self._vnf_descriptor_agent.project_id = project_id
        return self._vnf_descriptor_agent

    def get_market_agent(self, project_id):
        if self._market_agent is None:
            self._market_agent = MarketAgent(self._client, project_id=project_id)
        self._market_agent.project_id = project_id
        return self._market_agent

    def get_user_agent(self, project_id):
        if self._user_agent is None:
            self._user_agent = UserAgent(self._client, project_id=project_id)
        self._user_agent.project_id = project_id
        return self._user_agent

    def get_csarnsd_agent(self, project_id):
        if self._csarnsd_agent is None:
            self._csarnsd_agent = CSARNSDAgent(self._client, project_id=project_id)
        self._csarnsd_agent.project_id = project_id
        return self._csarnsd_agent

    def get_csarvnfd_agent(self, project_id):
        if self._csarvnfd_agent is None:
            self._csarvnfd_agent = CSARVNFDAgent(self._client, project_id=project_id)
        self._csarvnfd_agent.project_id = project_id
        return self._csarvnfd_agent

    def get_vnf_record_agent(self, project_id):
        self.get_ns_records_agent(project_id=project_id)
        if self._vnf_record_agent is None:
            self._vnf_record_agent = VNFRAgent(self._client, project_id=project_id, main_agent=self._ns_records_agent)
        self._vnf_record_agent.project_id = project_id
        return self._vnf_record_agent

    def get_vnf_package_agent(self, project_id):
        if self._vnf_package_agent is None:
            self._vnf_package_agent = VNFPackageAgent(self._client, project_id=project_id)
        self._vnf_package_agent.project_id = project_id
        return self._vnf_package_agent

    def get_key_agent(self, project_id):
        if self._key_agent is None:
            self._key_agent = KeyAgent(self._client, project_id=project_id)
        self._key_agent.project_id = project_id
        return self._key_agent

    def get_log_agent(self, project_id):
        if self._log_agent is None:
            self._log_agent = LogAgent(self._client, project_id=project_id)
        self._log_agent.project_id = project_id
        return self._log_agent

    def get_vnfci_agnet(self, project_id):
        if self._vnfci_agent is None:
            self._vnfci_agent = VNFCInstanceAgent(self._client, project_id=project_id)
        self._vnfci_agent.project_id = project_id
        return self._vnfci_agent

    def get_vdu_agnet(self, project_id):
        if self._vdu_agent is None:
            self._vdu_agent = VDUAgent(self._client, project_id=project_id,
                                       main_agent=self.get_ns_records_agent(project_id))
        self._vdu_agent.project_id = project_id
        return self._vdu_agent

    def get_service_agent(self, project_id):
        if self._service_agent is None:
            self._service_agent = ServiceAgent(self._client, project_id=project_id)
        return self._service_agent

    def get_agent(self, agent, project_id):
        if agent == "nsr":
            return self.get_ns_records_agent(project_id)
        if agent == "nsd":
            return self.get_ns_descriptor_agent(project_id)
        if agent == "vnfd":
            return self.get_vnf_descriptor_agent(project_id)
        if agent == "vnfr":
            return self.get_vnf_record_agent(project_id)
        if agent == "vim":
            return self.get_vim_instance_agent(project_id)
        if agent == "vnfpackage":
            return self.get_vnf_package_agent(project_id)
        if agent == "project":
            return self.get_project_agent()
        if agent == "event":
            return self.get_event_agent(project_id)
        if agent == "market":
            return self.get_market_agent(project_id)
        if agent == "user":
            return self.get_user_agent(project_id)
        if agent == "csarnsd":
            return self.get_csarnsd_agent(project_id)
        if agent == "csarvnfd":
            return self.get_csarvnfd_agent(project_id)
        if agent == "key":
            return self.get_key_agent(project_id)
        if agent == "log":
            return self.get_log_agent(project_id)
        if agent == 'vnfci':
            return self.get_vnfci_agnet(project_id)
        if agent == 'vdu':
            return self.get_vdu_agnet(project_id)
        if agent == "service":
            return self.get_service_agent(project_id)

        raise WrongParameters('Agent %s not found' % agent)
