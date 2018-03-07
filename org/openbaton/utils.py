from __future__ import print_function
import getopt
import logging
import os
import sys

import configparser


def get_config_parser(config_file_path, configparser=None):
    """
    Get the ConfigParser object containing the system configurations

    :return: ConfigParser object containing the system configurations
    """
    config = configparser.ConfigParser()
    if os.path.exists(config_file_path) and os.path.isfile(config_file_path):
        config.read(config_file_path)
        return config
    else:
        logging.error("Config file not found, please create %s" % config_file_path)
        return


def get_config(section, key, config_file_path, default=None):
    """
    Returns the ini property for section and key specified, using file in the specified location or the default value
    if not None

    :param section: the config parser section
    :param key: the config file key
    :param config_file_path: the path to the ini file
    :param default: the default value
    :return the value
    :raise IOError if no default and no file
    """
    config = get_config_parser(config_file_path)
    if not config:
        if default:
            return default
        else:
            raise IOError("File %s not found exception" % config_file_path)
    if default is None:
        return config.get(section=section, option=key)
    try:
        return config.get(section=section, option=key)
    except configparser.NoOptionError:
        return default


def get_vim_instance_test():
    return {
        "name": "vim-instance-test",
        "authUrl": 'http://test.test.ts',
        "tenant": 'test',
        "username": 'test',
        "password": 'test',
        "securityGroups": [
            'default'
        ],
        "type": "test",
        "location": {
            "name": "Test of nowhere",
            "latitude": "5.525876",
            "longitude": "31.314400"
        }
    }


def get_config_file_location():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f', longopts=["openbaton.file.location="])
    except getopt.GetoptError:
        return '/etc/openbaton/openbaton-sdk.ini'
    for o, a in opts:
        if o == '--openbaton.file.location':
            return a
    return '/etc/openbaton/openbaton-sdk.ini'


if __name__ == '__main__':
    print(get_config_file_location())
