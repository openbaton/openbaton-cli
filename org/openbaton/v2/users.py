import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Users(BaseObCmd):
    """Command to manage Users. It allows to:
        * show details of a specific User passing an id
        * list all saved Users
        * delete a specific User passing an id
        * create a specific User passing a path to a file or directly the json content
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "username", "email"]
    keys_to_exclude = ["password"]

    def find(self, params):
        if not params:
            return "ERROR: missing <user-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_user(_id),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <user> or <path-to-json>"
        user = parse_path_or_json(params[0])
        return result_to_str(get_result_to_show(self.app.ob_client.create_user(user),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def delete(self, params):
        if not params:
            return "ERROR: missing <username>"
        _id = params[0]
        self.app.ob_client.delete_user(_id)
        return "INFO: Deleted user with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_users(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)
