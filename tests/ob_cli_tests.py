import ConfigParser
import unittest

from org.openbaton.cli.openbaton import openbaton
from org.openbaton.sdk.client import OBClient


class MyTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        config = ConfigParser.ConfigParser()
        config.read('./nfvo.properties.ini')
        self.nfvo_ip = config.get('nfvo', 'nfvo_ip')
        self.nfvo_port = config.get('nfvo', 'nfvo_port')
        self.nfvo_username = config.get('nfvo', 'nfvo_username')
        self.nfvo_password = config.get('nfvo', 'nfvo_password')
        self.nfvo_project_id = config.get('nfvo', 'nfvo_project_id')
        super(MyTestCase, self).__init__(methodName)

    def test_cli(self):
        if True:
            return
        agent_choice = 'vnfci'
        action = 'create'
        params = [
            '{ "vnfComponent":{"connection_point":[{ "floatingIp":"random", "virtual_link_reference":"mgmt" }]}}',
            '69b73f73-745e-4138-ad35-320d26127c9a',
            'c1434dcb-2ab2-4138-bc21-308d225c9f9d',
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

    def test_ob_client(self):
        cl = OBClient(nfvo_ip=self.nfvo_ip,
                      nfvo_port=self.nfvo_port,
                      username=self.nfvo_username,
                      password=self.nfvo_password,
                      project_name="default",
                      https=False,
                      version=1)

        for p in cl.list_projects():
            print(p)


if __name__ == '__main__':
    unittest.main()
