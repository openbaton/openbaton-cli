ACTIONS = ["list", "show", "delete", "create", "update", "help"]

PRINT_FORMATS = ["table", "json", "yaml"]

AGENTS_ACTIONS = {
    "nsd": {
        "LIST_KEY": ["id", "name", "vendor", "version"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "vnfd": {
        "LIST_KEY": ["id", "name", "vendor", "version"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "nsr": {
        "LIST_KEY": ["id", "name", "status", "task", "vendor", "version", ],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": ["update", "upgrade", "execute", "add", "resume", "restart"]
    },
    "vnfr": {
        "LIST_KEY": ["id", "name", "vendor", "version", "status"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "vim": {
        "LIST_KEY": ["id", "name", "authUrl", "tenant", "username"],
        "EXCLUDE_KEY": ["password"],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": ["refresh"]
    },
    "project": {
        "LIST_KEY": ["id", "name", "description"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "event": {
        "LIST_KEY": ["id", "name", "networkServiceId", "virtualNetworkFunctionId", "type",
                     "endpoint"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "vnfpackage": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "csarnsd": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list", "show", "delete"],
        "ADDITIONAL_ACTIONS": []
    },
    "vnfci": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list"],
        "ADDITIONAL_ACTIONS": []
    },
    "csarvnfd": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list", "show", "delete"],
        "ADDITIONAL_ACTIONS": []
    },
    "key": {
        "LIST_KEY": ["id", "name", "fingerprint"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "log": {
        "LIST_KEY": ["id"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "vdu": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list", "create", "delete"],
        "ADDITIONAL_ACTIONS": []
    },  # vdu-vnfr
    "user": {
        "LIST_KEY": ["id", "username", "email"],
        "EXCLUDE_KEY": ["password"],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    },
    "market": {
        "LIST_KEY": ["id", "name", "vendor", "version"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list", "show", "delete"],
        "ADDITIONAL_ACTIONS": []
    },
    "service": {
        "LIST_KEY": ["id", "name"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["show"],
        "ADDITIONAL_ACTIONS": []
    },
    "script": {
        "LIST_KEY": ["id"],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": ["list", "create", "delete"],
        "ADDITIONAL_ACTIONS": []
    },
    "vdu-nsd": {
        "LIST_KEY": [],
        "EXCLUDE_KEY": [],
        "UNSUPPORTED_ACTIONS": [],
        "ADDITIONAL_ACTIONS": []
    }
}


def get_unsupported_action(agent_choice):
    return AGENTS_ACTIONS.get(agent_choice).get("UNSUPPORTED_ACTIONS")


def get_list_key(agent_choice):
    return AGENTS_ACTIONS.get(agent_choice).get("LIST_KEY")


def get_excluded_key(agent_choice):
    return AGENTS_ACTIONS.get(agent_choice).get("EXCLUDE_KEY")


def get_additional_action(agent_choice):
    return AGENTS_ACTIONS.get(agent_choice).get("ADDITIONAL_ACTIONS")


def get_agents():
    return AGENTS_ACTIONS.keys()
