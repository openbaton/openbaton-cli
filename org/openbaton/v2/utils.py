import json

import tabulate


def get_result_to_list(values, keys, _format='table'):
    if _format == 'json':
        return values
    res = [keys]
    for x in values:
        tmp = []
        for key in keys:
            val = x.get(key)
            if isinstance(val, dict):
                if val.get('name'):
                    tmp.append(val.get('name'))
                else:
                    tmp.append(val.get('id'))
            else:
                tmp.append(val)
        res.append(tmp)
    return res


def get_result_to_show(obj, excluded_keys, _format='table'):
    if _format == 'table':
        result = [["key", "value"]]
        for k, v in obj.items():
            if k not in excluded_keys:
                if isinstance(v, list):
                    if len(v) > 0:
                        tmp = []
                        if isinstance(v[0], dict):
                            tmp.append(" values: \n")
                            tmp.extend(["- " + (x.get('ip') or x.get("id")) for x in v])
                        result.append([k, "\n".join(tmp)])
                else:
                    if isinstance(v, dict):
                        id_name = v.get("name")
                        if id_name is None:
                            id_name = v.get("id")
                        result.append([k, id_name])
                    else:
                        result.append([k, v])

        return sorted(result)
    elif _format == 'json':
        return obj


def parse_path_or_json(path_or_json):
    path_or_json = path_or_json.strip()
    if path_or_json.startswith("{"):
        return json.loads(path_or_json)
    with open(path_or_json, "r") as f:
        return json.loads(f.read())


def result_to_str(result, _format='table'):
    if _format == "table":
        return tabulate.tabulate(result, headers="firstrow", tablefmt="grid")
    elif _format == "json":
        return json.dumps(result, indent=4)
