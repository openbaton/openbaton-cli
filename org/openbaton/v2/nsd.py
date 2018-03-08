import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Nsd(BaseObCmd):
    """Command to manage NSDs. It allows to:
        * show details of a specific NSD passing an id
        * list all saved NSDs
        * delete a specific NSD passing an id
        * create a specific NSD passing a path to a file or directly the json content
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "vendor", "version"]
    keys_to_exclude = []

    def find(self, params):
        if not params:
            return "ERROR: missing <nsd-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_nsd(_id),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <nsd> or <path-to-json>"
        nsd = parse_path_or_json(params[0])
        return result_to_str(get_result_to_show(self.app.ob_client.create_nsd(nsd),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def delete(self, params):
        if not params:
            return "ERROR: missing <nsd-id>"
        _id = params[0]
        self.app.ob_client.delete_nsd(_id)
        return "INFO: Deleted nsd with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_nsds(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)
