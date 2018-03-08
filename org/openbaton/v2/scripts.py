import logging

from org.openbaton.v2.cmd import BaseObCmd
from org.openbaton.v2.errors import ActionNotSupported
from org.openbaton.v2.utils import get_result_to_list, get_result_to_show, parse_path_or_json, result_to_str


class Scripts(BaseObCmd):
    """Command to manage Scripts. It allows to:
        * show a Script passing an id
    """

    log = logging.getLogger(__name__)
    keys_to_list = ["id", "name", "vendor", "version"]
    keys_to_exclude = []

    def find(self, params):
        if not params:
            return "ERROR: missing <script-id>"
        script_id = params[0]
        return "".join(chr(i) for i in self.app.ob_client.get_script(script_id).get("payload"))

    def create(self, params):
        raise ActionNotSupported("Action 'create' is not supported")

    def delete(self, params):
        raise ActionNotSupported("Action 'delete' is not supported")

    def list(self, params=None):
        raise ActionNotSupported("Action 'list' is not supported")
