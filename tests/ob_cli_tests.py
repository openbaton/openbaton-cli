import ConfigParser
import unittest

from org.openbaton.cli.openbaton import openbaton


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

    def test_generate_key(self):
        agent_choice = 'log'
        action = 'show'
        params = 'ed04ddcb-a824-4e70-9e35-0b9aa3a08f50 iperf-server iperf-server-6319228'
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
