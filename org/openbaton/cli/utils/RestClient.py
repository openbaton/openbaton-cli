import base64
import json
import logging

import requests

logger = logging.getLogger("org.openbaton.cli.RestClient")


def _expired_token(content):
    if content is not None:
        if "error" in content:
            try:
                return json.loads(content).get("error") is not None and json.loads(content).get(
                    "error") == "invalid_token"
            except AttributeError:
                return False
    return False


class RestClient(object):
    def __init__(self, nfvo_ip="localhost", nfvo_port="8080", https=False, version=1, username=None, password=None,
                 project_id=None):

        if https:
            self.base_url = "https://%s:%s/" % (nfvo_ip, nfvo_port)
        else:
            self.base_url = "http://%s:%s/" % (nfvo_ip, nfvo_port)

        self.ob_url = "%sapi/v%s/" % (self.base_url, version)

        self.project_id = project_id
        self.token = None
        self.username = username
        self.password = password
        # print "user %s" % username

    def get(self, url):
        if self.token is None:
            self.token = self._get_token()
        headers = {
            "Authorization": "Bearer %s" % self.token,
            "accept": "application/json",
            "content-type": "application/json"
        }
        if self.project_id is not None:
            headers["project-id"] = self.project_id
        final_url = self.ob_url + url
        # print "executing get on url %s, with headers: %s" % (final_url, headers)
        response = requests.get(final_url, headers=headers)
        result = response.text
        if _expired_token(result):
            self.token = self._get_token()
            self.get(url)
        if result == "":
            result = '{"error":"Not found"}'
        return result

    def post(self, url, body, headers=None):
        if self.token is None:
            self.token = self._get_token()
        if headers is None:
            headers = {"content-type": "application/json"}
        if self.project_id is not None:
            headers["project-id"] = self.project_id

        headers["Authorization"] = "Bearer %s" % self.token

        response = requests.post(self.ob_url + url, data=body, headers=headers)

        if _expired_token(response.text):
            self.token = self._get_token()
            self.post(url, body, headers=headers)
        return response.text

    def post_file(self, url, _file, headers=None):
        if self.token is None:
            self.token = self._get_token()
        if headers is None:
            headers = {
                "Authorization": "Bearer %s" % self.token,
                "accept": "application/json",
                "project-id": self.project_id
            }
        files = {'file': ('file', _file, "multipart/form-data")}

        ses = requests.session()

        response = ses.post(self.ob_url + url, files=files, headers=headers)
        return response.text

    def put(self, url, body, headers=None):
        if self.token is None:
            self.token = self._get_token()
        if headers is None:
            headers = {"content-type": "application/json"}
        if self.project_id is not None:
            headers["project-id"] = self.project_id
        headers["Authorization"] = "Bearer %s" % self.token
        response = requests.put(self.ob_url + url, data=body, headers=headers)
        if _expired_token(response.text):
            self.token = self._get_token()
            self.put(url, body=body, headers=headers)
        return response.text

    def delete(self, url):
        if self.token is None:
            self.token = self._get_token()
        headers = {}
        if self.project_id is not None:
            headers = {"project-id": self.project_id}
        headers["Authorization"] = "Bearer %s" % self.token
        (resp_headers, content) = self.client.request(self.ob_url + url, "DELETE", headers=headers)
        if _expired_token(content):
            self.token = self._get_token()
            self.delete(url)
        return content

    def _get_token(self):
        logger.debug("Executing post: %s" % (self.base_url + "oauth/token"))
        h = {"Authorization": "Basic %s" % base64.b64encode("openbatonOSClient:secret"),
             "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        logger.debug("Headers are: %s" % h)
        response = requests.post(self.base_url + "oauth/token",
                                 headers=h,
                                 data="username=%s&password=%s&grant_type=password" % (
                                     self.username, self.password))
        logger.debug(response.text)
        token = json.loads(response.text).get("value")
        logger.debug("Got token %s" % token)
        return token