import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class VnfPackages(BaseObCmd):
    """Command to manage VNFPackages. It allows to:
        * show details of a specific VNFPackage passing an id
        * list all saved VNFPackages
        * delete a specific VNFPackage passing an id
        * create a specific VNFPackage passing a path to a file or directly the json content
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name"]
    keys_to_exclude = []

    def find(self, params):
        if not params:
            return "ERROR: missing <package-id>"
        _id = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.get_package(_id),
                                                     excluded_keys=self.keys_to_exclude,
                                                     _format=self.app.format))

    def create(self, params):
        if not params:
            return "ERROR: missing <path-to-package>"
        package = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.create_package(package),
                                                     excluded_keys=self.keys_to_exclude,
                                                     _format=self.app.format))

    def delete(self, params):
        if not params:
            return "ERROR: missing <package-id>"
        _id = params[0]
        self.app.ob_client.delete_package(_id)
        return "INFO: Deleted package with id %s" % _id

    def list(self, params=None):
        return result_to_str(
            get_result_to_list(self.app.ob_client.list_packages(), keys=self.keys_to_list, _format=self.app.format),
            _format=self.app.format)
