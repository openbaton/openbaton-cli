import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Vims(BaseObCmd):
    """Command to manage VimInstances. It allows to:
        * show details of a specific VimInstance passing an id
        * list all saved VimInstances
        * delete a specific VimInstance passing an id
        * create a specific VimInstance passing a path to a file or directly the json content
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "authUrl"]
    keys_to_exclude = ["password"]

    def refresh(self, params):
        if not params:
            return "ERROR: missing <vim-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.refresh_vim(_id),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def handle_special_action(self, action, params):
        if action == 'refresh':
            return self.refresh(params)
        else:
            return super(BaseObCmd, self).handle_special_action(action, params)

    def find(self, params):
        if not params:
            return "ERROR: missing <vim-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_vim(_id),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <vim> or <path-to-json>"
        vim = parse_path_or_json(params[0])
        return result_to_str(get_result_to_show(self.app.ob_client.create_vim(vim),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def delete(self, params):
        if not params:
            return "ERROR: missing <vim-id>"
        _id = params[0]
        self.app.ob_client.delete_vim(_id)
        return "INFO: Deleted vim with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_vims(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)
