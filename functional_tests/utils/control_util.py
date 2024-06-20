# Copyright 2024 Broadcom. All Rights Reserved.
import json
import subprocess
from collections.abc import Iterable

import jinja2


def render_template(control_template, values_dict, control_name, template_variable):
    """
    Print out control name, compliance template, template variable name and values
    They are very useful in triaging the issues in compliance values and drift value configurations
    :param control_template: control compliance template.
    :type: Dict
    :param values_dict, template variable values dictionary
    :type: Dict
    :param control_name, control name
    :type: str
    :param template_variable: control template variable name
    :type: str
    """
    print(f"{control_name} control_template: {control_template}\n")
    template_data = values_dict[template_variable] if template_variable in values_dict else None
    print(f"{control_name} template_variable: {template_variable} = {template_data}\n")
    environment = jinja2.Environment()
    template = environment.from_string(control_template)
    if template_data is not None:
        return json.loads(template.render(values_dict))
    else:
        return None


def get_ssl_thumbprint_sha1(host_ip):
    """
    Get ssl sha1 thumb print
    :param host_ip: host ip address
    :type: str
    :return: thumb print
    :type: str
    """

    cmd = f"echo -n|openssl s_client -connect {host_ip}:443 2>/dev/null|openssl x509 -noout -fingerprint -sha1"
    output = subprocess.getoutput(cmd)
    outputs = output.split("=")
    return outputs[1] if len(outputs) > 1 else ""


def find_and_replace_value(dictionary, key, value):
    """
    Find and replace all values in a dictionary by searching the key first
    :param dictionary: dictionary
    :type: Dict
    :param key: dictionary key
    :type: str
    :param value: value of the key in the dictionary
    :type: str
    :return: dictionary with replaced values
    :type: Dict
    """

    if isinstance(dictionary, dict):
        for k, v in dictionary.items():
            if k == key:
                dictionary[k] = value
                break
            else:
                if isinstance(v, dict):
                    find_and_replace_value(v, key, value)
                elif isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            find_and_replace_value(i, key, value)
    return dictionary


def find_value(search_key, obj):
    """
    Find value of the key in a dictionary
    :param obj: dictionary
    :type: Dict
    :param search_key: dictionary key
    :type: str
    :return: value of the search key
    :type: str
    """
    try:
        if isinstance(obj, dict):
            for key, value in obj.items():  # dict?
                if search_key == key:
                    return value
                elif not is_primitive(value):
                    result = find_value(search_key, value)
                    if result is not None:
                        return result

        if isinstance(obj, Iterable):
            for item in obj:  # iterable?
                if not is_primitive(item):
                    result = find_value(search_key, item)
                    if result is not None:
                        return result
    except (AttributeError, TypeError) as e:
        print(f"Error {e}\n")
        pass

    return None


def find_key(search_key, obj):
    """
    Find value of the key in a dictionary
    :param obj: dictionary
    :type: Dict
    :param search_key: dictionary key
    :type: str
    :return: value of the search key
    :type: str
    """
    try:
        if isinstance(obj, dict):
            for key, value in obj.items():  # dict?
                if search_key == key:
                    return key
                elif not is_primitive(value):
                    result = find_value(search_key, value)
                    if result is not None:
                        return result

        if isinstance(obj, Iterable):
            for item in obj:  # iterable?
                if not is_primitive(item):
                    result = find_value(search_key, item)
                    if result is not None:
                        return result
    except (AttributeError, TypeError) as e:
        print(f"Error {e}\n")
        pass

    return None


primitives = (bool, str, int, float, type(None))


def is_primitive(obj):
    """
    check if the obj is a primitive type
    :param obj: object instance
    :type: Any
    :return: if the obj is primitive
    :type: bool
    """
    return type(obj) in primitives
