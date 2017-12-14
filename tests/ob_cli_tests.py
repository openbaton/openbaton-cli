import ConfigParser
import logging
import unittest

import sys

from org.openbaton.cli.openbaton import openbaton

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

class MyTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        config = ConfigParser.ConfigParser()
        config.read('tests/nfvo.properties.ini')
        self.nfvo_ip = config.get('nfvo', 'nfvo_ip')
        self.nfvo_port = config.get('nfvo', 'nfvo_port')
        self.nfvo_username = config.get('nfvo', 'nfvo_username')
        self.nfvo_password = config.get('nfvo', 'nfvo_password')
        self.nfvo_project_id = config.get('nfvo', 'nfvo_project_id')
        super(MyTestCase, self).__init__(methodName)

    def test_scale_out(self, params=""):
        logging.basicConfig(level=logging.DEBUG)
        agent_choice = 'vnfpackage'
        action = 'update'
        params = [
            'a19684cd-5914-4ae8-b3fa-4623ca8d3f4d',
            # 'type=lxd'
             # '{"securityGroup":"default"}'
        ]
        openbaton(agent_choice=agent_choice,
                  action=action,
                  params=params,
                  project_id=self.nfvo_project_id,
                  username=self.nfvo_username,
                  password=self.nfvo_password,
                  nfvo_ip=self.nfvo_ip,
                  nfvo_port=self.nfvo_port)
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
