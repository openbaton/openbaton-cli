import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Keys(BaseObCmd):
    """Command to manage keys: it is possible to:

        * show details of a specific key passing an id
        * list all saved keys
        * delete a specific key passing an id
        * create a specific key passing the key name
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "fingerprint"]
    keys_to_exclude = []

    def find(self, params):
        if not params:
            return "ERROR: missing <key-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_key(_id),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <key-name>"
        key = params[0]
        return self.app.ob_client.create_key(key)

    def delete(self, params):
        if not params:
            return "ERROR: missing <nsd-id>"
        _id = params[0]
        self.app.ob_client.delete_key(_id)
        return "INFO: Deleted nsd with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_keys(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)

    def import_key(self, params):
        if len(params) < 2:
            return "ERROR: missing <key-name> and <pub-key>"
        key_name = params[0]
        ssh_pub_key = params[1]
        return self.app.ob_client.import_key(key_name, ssh_pub_key)

    def handle_special_action(self, action, params):
        if action == "import":
            return self.import_key(params)
        return super(BaseObCmd, self).handle_special_action(action, params)
