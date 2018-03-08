import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Projects(BaseObCmd):
    """Command to manage Projects. It allows to:
        * show details of a specific Project passing an id
        * list all saved Projects
        * delete a specific Project passing an id
        * create a specific Project passing a path to a file or directly the json content
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "description"]
    keys_to_exclude = []

    def find(self, params):
        if not params:
            return "ERROR: missing <project-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_project(_id),
                                                     excluded_keys=self.keys_to_exclude,
                                                     _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <project> or <path-to-json>"
        project = parse_path_or_json(params[0])
        return result_to_str(get_result_to_show(self.app.ob_client.create_project(project),
                                                     excluded_keys=self.keys_to_exclude,
                                                     _format=self.app.format))

    def delete(self, params):
        if not params:
            return "ERROR: missing <project-id>"
        _id = params[0]
        self.app.ob_client.delete_project(_id)
        return "INFO: Deleted nsd with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_projects(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)
