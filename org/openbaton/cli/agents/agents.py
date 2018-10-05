from __future__ import print_function

import json
import os

from org.openbaton.cli.errors.errors import WrongParameters, NotFoundException, SdkException
from org.openbaton.cli.utils.RestClient import RestClient

WRONG_UPDATE_TYPES = [dict, list]


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


def _cast(correct_type, new_entity):
    if correct_type == bool:

        true_ = new_entity.lower() == 'true'
        false_ = new_entity.lower() == 'false'
        if true_:
            return true_
        if false_:
            return not false_
        else:
            raise SdkException("Boolean value can only be 'true' or 'false'")
    else:
        return correct_type(new_entity)


def _format_update_value(entity):
    # entitiy can be either a json or a str like key=value,key2=value2 or a list like key=value key=value
    new_entity = {}
    if len(entity) == 1:
        entity = entity[0]
        if entity.endswith("}") or entity.endswith("]"):
            new_entity = json.loads(entity)
        else:  # for a single key = value
            new_entity = {entity.split("=")[0]: entity.split("=")[1]}
    else:  # sure key=vale key1=value1
        for val in entity:
            new_entity[val.split("=")[0]] = (val.split("=")[1])
    return new_entity


def _update_entity(old_value, entity):
    try:
        new_entity = _format_update_value(entity)
    except:
        raise SdkException('The passed JSON seems to be invalid.')

    for k, v in new_entity.items():
        if k in old_value:
            if type(old_value[k]) in WRONG_UPDATE_TYPES:
                raise SdkException('Cannot update a sub object, execute update directly to that entity')

            if isinstance(old_value[k], type(new_entity[k])):
                old_value[k] = new_entity[k]
            else:
                correct_type = type(old_value[k])
                new_entity[k] = _cast(correct_type, new_entity[k])
                old_value[k] = new_entity[k]
        else:
            raise SdkException('Key does not exist for the entity.')
    return old_value


class BaseAgent(object):
    def __init__(self, client, url, agent_name, project_id=None):
        self._client = client
        self.url = url
        if project_id is not None:
            self._client.project_id = project_id
        self._type = self.__class__.__name__
        self.agent = agent_name

    def find(self, _id=""):
        return self._client.get(self.url + "/%s" % _id)

    def delete(self, _id):
        self._client.delete(self.url + "/%s" % _id)

    def update(self, _id, entity):
        old_value = json.loads(self._client.get(self.url + "/%s" % _id))
        old_value = _update_entity(old_value, entity)
        return json.loads(self._client.put(self.url + "/%s" % _id, json.dumps(old_value)))

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

    def execute_action(self, action, *params):
        result = getattr(self, action)(params)
        if type(result) is str or type(result) is unicode:
            result = json.loads(result)
        return result

    def help(self, *params):
        return {
            "list": "openbaton %s list:  show all entities" % self.agent,
            "show": "openbaton %s show <id>: show details of selected id" % self.agent,
            "create": "openbaton %s create <object>: creates an entity with passed vaule" % self.agent,
            "update": "openbaton %s update <id> <key>=<value> [ .. <key>=<value> ]: updates an entity with passed values" % self.agent,
            "help": "openbaton %s help: shows the agent %s help" % (self.agent, self.agent),
        }


class ProjectAgent(BaseAgent):
    def __init__(self, client):
        super(ProjectAgent, self).__init__(client, "projects", 'project')


class EventAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(EventAgent, self).__init__(client, "events", 'event', project_id=project_id)


class VimInstanceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VimInstanceAgent, self).__init__(client, "datacenters", 'vim', project_id=project_id)

    def refresh(self, _id):
        return self._client.get(self.url + "/%s/refresh" % _id)


class NSRAgent(BaseAgent):
    def create(self, entity='', _id="{}"):
        entity = entity.strip()
        return json.loads(self._client.post(self.url + "/%s" % entity, json.dumps(json.loads(_id))))

    def update(self, nsr_id='', vnfr_id='', _id="{}"):
        vnfr= vnfr_id[0]
        return (self._client.post(self.url + "/%s/vnfrecords/%s/update" % (nsr_id, vnfr), json.dumps(json.loads(_id))))

    def upgrade(self, entity='', nsr_id='', vnfr_id='', _id="{}"):
        nsr_id= entity[0]
        vnfr_id = entity[1]
        param=entity[2:]
        if(param==()):
            body = "{}"
        else:
            try:
                body = param[0]
            except:
                raise SdkException('The passed JSON seems to be invalid.')
        return json.dumps(self._client.post(self.url + "/%s/vnfrecords/%s/upgrade" % (nsr_id, vnfr_id), body))

    def restart(self, entity='', nsr_id='', vnfr_id='', _id="{}"):
        nsr_id= entity[0]
        vnfr_id = entity[1]
        param=entity[2:]
        if(param==()):
            body = "{}"
        else:
            try:
                body = param[0]
            except:
                raise SdkException('The passed JSON seems to be invalid.')
        return self._client.post(self.url + "/%s/vnfrecords/%s/restart" % (nsr_id, vnfr_id), body)

    def execute(self, entity='', nsr_id='', vnfr_id='', _id="{}"):
        vnfr= vnfr_id[0]
        return json.loads(self._client.post(self.url + "/%s/vnfrecords/%s/execute-script" % (nsr_id, vnfr_id), entity, json.dumps(json.loads(_id))))

    def add(self, entity='', nsr_id='', vnfd_id='', _id="{}"):
        nsr_id= entity[0]
        vnfd_id = entity[1]
        param=entity[2:]
        if(param==()):
            body = "{}"
        else:
            try:
                body = param[0]
            except:
                raise SdkException('The passed JSON seems to be invalid.')
        return self._client.put(self.url + "/%s/vnfd/%s" % (nsr_id, vnfd_id), body)

    def resume(self, nsr_id='', _id="{}"):
        return (self._client.post(self.url + "/%s/resume" % (nsr_id), json.dumps(json.loads(_id))))

    def __init__(self, client, project_id):
        super(NSRAgent, self).__init__(client, "ns-records", 'nsr', project_id=project_id)


class VNFCInstanceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFCInstanceAgent, self).__init__(client, "ns-records", 'vnfci', project_id=project_id)

    # {id}/vnfrecords/{idVnf}/vdunits/vnfcinstances
    def delete(self, nsr_id, vnfr_id, vdu_id="", vnfci_id=""):
        return self._client.delete(
            "%s/%s/vnfrecords/%s/vdunits/%s/vnfcinstances/%s" % (self.url, nsr_id, vnfr_id, vdu_id, vnfci_id))

    def create(self, entity, nsr_id, vnfr_id, vdu_id="", standby=False):
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
        if os.path.exists(entity) and os.path.isfile(entity):
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
        super(KeyAgent, self).__init__(client, "keys", 'key', project_id=project_id)


class UserAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(UserAgent, self).__init__(client, "users", 'user', project_id=project_id)


class ServiceAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(ServiceAgent, self).__init__(client, "components/services", 'ServiceCredentials', project_id=project_id)

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
        super(MarketAgent, self).__init__(client, "ns-descriptors/marketdownload", 'market', project_id=project_id)

    def help(self, *params):
        return {
            "create": "openbaton %s create <link>: create a nsd from maketplace link" % self.agent
        }


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
        super(LogAgent, self).__init__(client, "logs", "log", project_id=project_id)


class NSDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(NSDAgent, self).__init__(client, "ns-descriptors", "nsd", project_id=project_id)


class VNFPackageAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(VNFPackageAgent, self).__init__(client, "vnf-packages", "vnfpackage", project_id=project_id)

    def create(self, entity='', _id=""):
        if os.path.exists(entity) and os.path.isfile(entity) and entity.endswith(".tar"):
            return json.loads(self._client.post_file(self.url + "/%s" % _id, open(entity, "rb")))


class CSARNSDAgent(BaseAgent):
    def __init__(self, client, project_id):
        super(CSARNSDAgent, self).__init__(client, "csar-nsd", "csarnsd", project_id=project_id)

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
        super(CSARVNFDAgent, self).__init__(client, "csar-vnfd", "csarvfnd", project_id=project_id)

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
        super(VNFDAgent, self).__init__(client=client, url="vnf-descriptors", agent_name="vnfd", project_id=project_id)


class SubAgent(BaseAgent):
    def __init__(self, client, project_id, agent_name, main_agent, sub_url, sub_obj):
        super(SubAgent, self).__init__(client, main_agent.url, agent_name, project_id=project_id)
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


class ScriptAgent(SubAgent):
    def __init__(self, client, project_id, main_agent):
        super(ScriptAgent, self).__init__(client=client,
                                          project_id=project_id,
                                          agent_name="script",
                                          main_agent=main_agent,
                                          sub_url="scripts",
                                          sub_obj="scripts")

    def update(self, _id, entity):
        file_path = entity[0]
        vnfpackage_id, script = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path) as f:
                file_content = json.dumps(f.read().replace('\n', ''))
                try:
                    entity_json = json.loads(file_content)
                except:
                    raise SdkException('The passed JSON seems to be invalid.')
            response = self._client.put_file("{}/{}/{}/{}".format(self.url, vnfpackage_id, self.sub_url, _id),
                                             entity_json)
            script['payload'] = json.dumps(response)
            return script
        else:
            raise WrongParameters("{} is not a file".format(file_path))


class VNFRAgent(SubAgent):
    def __init__(self, client, project_id, main_agent):
        super(VNFRAgent, self).__init__(client=client,
                                        project_id=project_id,
                                        main_agent=main_agent,
                                        agent_name="vnfr",
                                        sub_url='vnfrecords',
                                        sub_obj="vnfr")


class VDUAgent(SubAgent):
    def __init__(self, client, project_id, main_agent):
        if main_agent.url == "ns-records":
            super(VDUAgent, self).__init__(client=client,
                                           project_id=project_id,
                                           main_agent=main_agent,
                                           sub_url='vnfrecords',
                                           agent_name="vdu-vnfr",
                                           sub_obj="vnfr")
        else:  # main_agent == "ns-descriptors"
            super(VDUAgent, self).__init__(client=client,
                                           project_id=project_id,
                                           main_agent=main_agent,
                                           sub_url='vnfdescriptors',
                                           agent_name="vdu",
                                           sub_obj="vnfd")

    def find(self, _id=""):
        if _id is None or _id == "":
            raise WrongParameters("Please provide the id, only action show is allowed on this agent")
        if self._main_agent.url == "ns-records":
            nsr_id, vnfr_id, vdu = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj, 'vdu')
        else:  # self._main_agent == "ns-descriptors"
            nsd_id, vnfd_id, vdu = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj, 'vdu')
        return json.dumps(vdu)

    def update(self, _id, entity):
        if self._main_agent.url == "ns-records":
            nsr_id, vnfr_id, vdu = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj, 'vdu')
            url = self.url + "/" + nsr_id + "/" + self.sub_url + "/" + vnfr_id + "/" + "vdus/" + _id
        else:  # self._main_agent == "ns-descriptors"
            nsd_id, vnfd_id, vdu = _get_parents_obj_id_from_id(_id, self._main_agent, self.sub_obj, 'vdu')
            url = self.url + "/" + nsd_id + "/" + self.sub_url + "/" + vnfd_id + "/" + "vdus/" + _id
        old_value = _update_entity(vdu, entity)
        return json.loads(self._client.put(url, json.dumps(old_value)))


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
        self._script_agent = None

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

    def get_vdu_agnet(self, project_id, parent):
        if self._vdu_agent is None:
            if parent == "nsr":
                self._vdu_agent = VDUAgent(self._client, project_id=project_id,
                                           main_agent=self.get_ns_records_agent(project_id))
            else:  # if parent == "nsd"
                self._vdu_agent = VDUAgent(self._client, project_id=project_id,
                                           main_agent=self.get_ns_descriptor_agent(project_id))
        self._vdu_agent.project_id = project_id
        return self._vdu_agent

    def get_service_agent(self, project_id):
        if self._service_agent is None:
            self._service_agent = ServiceAgent(self._client, project_id=project_id)
        return self._service_agent

    def get_script_agent(self, project_id):
        if self._script_agent is None:
            self._script_agent = ScriptAgent(self._client, project_id=project_id,
                                             main_agent=self.get_vnf_package_agent(project_id))
            self._script_agent.project_id = project_id
            return self._script_agent

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
        if "-" in agent and agent.split("-")[0] == 'vdu':  # vdu-nsd
            return self.get_vdu_agnet(project_id, agent.split("-")[1])
        if agent == "vdu":  # vdu-nsr
            return self.get_vdu_agnet(project_id, "nsr")
        if agent == "service":
            return self.get_service_agent(project_id)
        if agent == "script":
            return self.get_script_agent(project_id)
        raise WrongParameters('Agent %s not found' % agent)
