try:
   import ConfigParser
except ImportError:
    import configparser as ConfigParser

# import ConfigParser
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
        agent_choice = 'vdu-vnfd'
        action = 'show'
        params = [
                # '7f79c678-2bb5-4f11-a2f2-533967a1a487'   #vdu-vnfr
                'dfb1cfa9-43b2-4790-86b7-7023bbf47afd'    #vdu-vnfd
                # ,'shared=true'
            #,'{"securityGroup":"default"}'
        ]
        openbaton(agent_choice=agent_choice,
                  action=action,
                  params=params,
                  project_id=self.nfvo_project_id,
                  username= self.nfvo_username,
                  password=self.nfvo_password,
                  nfvo_ip=self.nfvo_ip,
                  nfvo_port=self.nfvo_port)
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
