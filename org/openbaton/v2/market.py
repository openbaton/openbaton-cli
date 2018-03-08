import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.errors import ActionNotSupported
from org.openbaton.v2.utils import get_result_to_show, result_to_str


class Market(BaseObCmd):
    """Command to manage nsd from the marketplace. Allows to create a NSD by passing a marketplace link
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "vendor", "version"]
    keys_to_exclude = []

    def find(self, params):
        raise ActionNotSupported("Action 'show' is not supported")

    def create(self, params):
        if not params:
            return "ERROR: missing <marketplace-link>"
        link = params[0]
        return result_to_str(get_result_to_show(self.app.ob_client.create_nsd_from_market(link),
                                                excluded_keys=self.keys_to_exclude,
                                                _format=self.app.format))

    def delete(self, params):
        raise ActionNotSupported("Action 'delete' is not supported")

    def list(self, params=None):
        raise ActionNotSupported("Action 'list' is not supported")
