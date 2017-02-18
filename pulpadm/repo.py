from __future__ import print_function, unicode_literals
import re
import sys
import json
import logging
from urlparse import urlparse
import requests
from requests.auth import HTTPBasicAuth
import pulpadm.utils as utils
from pulpadm.constants import API_PATH, MAX_SPEED


# Disable urllib3 warnings at the top-level
requests.packages.urllib3.disable_warnings()


class RPMRepo:
    """
    Create RPM repo object

    :param hostname str: pulp server hostname
    :param port int: pulp server RESTful HTTP port
    :param username str: pulp server account username
    :param password str: pulp server account password

    """
    def __init__(self, hostname=None, port=None, username=None, password=None):
        self.logger = logging.getLogger(__name__ + '.RPMRepo')
        self.logger.debug("Initiate RPMRepo object")

        # Pulp Server url & auth
        self.url = "https://{0}:{1}/{2}".format(hostname, port, API_PATH["repo"])
        self.auth = HTTPBasicAuth(username, password)

    def generate_repo_create(self, repo_id=None, **kwargs):
        """
        Generates a create repository API object. Config keywords are as follow:

        display_name (str)  User-readable display name (i18n characters)
        feed (str)          URL of the external source repository to sync
        max_speed (int)     Maximum bandwidth used per download thread (bytes/sec)
        relative_url (str)  Relative path the repository will be served from
        serve_http (bool)   Enable/Disable HTTP Serve
        serve_https (bool)  Enable/Disable HTTPS Serve
        feed_ca_cert (str)  Full path to the CA certificate that should be used
                            to verify the external repo server's SSL certificate
        feed_cert (str)     Full path to the certificate to use for authorization
                            when accessing the external feed
        feed_key (str)      Full path to the private key for feed_cert
        proxy_host (str)    Proxy server url to use
        proxy_port (int)    Port on the proxy server to make requests


        :param repo_id str: the repository id
        :param kwargs: the repository config information
        :return: create repository API object
        :rtype: dict

        """
        if repo_id is not None:
            # Set defaults
            feed = kwargs.get("feed", None)
            relative_url = kwargs.get("relative_url", None)
            max_speed = kwargs.get("max_speed", None)

            if relative_url is None and feed is None:
                relative_url = "{0}/".format(repo_id)
            elif relative_url is None and feed is not None:
                relative_url = urlparse(feed).path

            if max_speed is None and feed is not None:
                max_speed = MAX_SPEED

            # Return API object
            return {
                "id": repo_id,
                "display_name": kwargs.get("display_name", None),
                "notes": {
                    "_repo-type": "rpm-repo"
                },
                "importer_type_id": "yum_importer",
                "importer_config": {
                    "feed": kwargs.get("feed", None),
                    "max_speed": max_speed,
                    "proxy_host": kwargs.get("proxy_host", None),
                    "proxy_port": kwargs.get("proxy_port", None),
                    "ssl_ca_cert": utils.read_file(kwargs.get("feed_ca_cert", None)),
                    "ssl_client_cert": utils.read_file(kwargs.get("feed_cert", None)),
                    "ssl_client_key": utils.read_file(kwargs.get("feed_key", None))
                },
                "distributors": [
                    {
                        "distributor_id": "yum_distributor",
                        "distributor_type_id": "yum_distributor",
                        "distributor_config": {
                            "http": kwargs.get("serve_http", True),
                            "https": kwargs.get("serve_https", True),
                            "relative_url": re.sub("^/+", "", relative_url)
                        },
                        "auto_publish": True
                    },
                    {
                        "distributor_id": "export_distributor",
                        "distributor_type_id": "export_distributor",
                        "distributor_config": {
                            "http": kwargs.get("serve_http", True),
                            "https": kwargs.get("serve_https", True),
                            "relative_url": re.sub("^/+", "", relative_url)
                        },
                        "auto_publish": False
                    }
                ]
            }
        else:
            return {}

    def get(self, repo_id=None, details=False):
        """
        Retrieves information on all repositories (single repository if repo_id
        is given). The returned data includes general repository metadata,
        metadata describing any importers and distributors associated with it,
        and a count of how many content units have been stored locally for the
        repository.

        :param repo_id str: the repository id
        :param details bool: whether to include distributors, importers and
                             content unit
        :return: repository information
        :rtype: list

        """
        logger = logging.getLogger(__name__ + ".get")

        # API request
        r = requests.get(
            self.url + repo_id + "/" if repo_id else self.url,
            auth=self.auth, verify=False,
            params={"details": details},
            headers={"Content-Type": "application/json"}
        )

        # Error handlers
        if r.status_code == 404:
            msg = "Repository [{0}] does not exist".format(repo_id)
            #  msg = r.json()["error"].get("description", "Unknown")
            logger.error("\033[0;31m" + msg + "\033[0m")
            sys.exit(r.status_code)

        # Return object
        if repo_id is not None:
            return [r.json()]
        else:
            return r.json()

    def create(self, repo_config=None):
        """
        Creates a new repository

        :param repo_config dict: create repository API object
                                 //see generate_repo_create() method for more
                                 details//
        :return: None

        """
        logger = logging.getLogger(__name__ + ".create")

        # API request
        if repo_config:
            r = requests.post(
                self.url, auth=self.auth, verify=False,
                data=json.dumps(repo_config),
                headers={"Content-Type": "application/json"}
            )

            # Error handlers
            repo_id = repo_config["id"]
            if r.status_code == 201:
                msg = "Successfully created repository [{0}]".format(repo_id)
                logger.info(msg)
            elif r.status_code == 409:
                msg = "A repository with Id [{0}] already exists".format(repo_id)
                logger.error("\033[0;31m" + msg + "\033[0m")
                sys.exit(r.status_code)
            else:
                msg = r.json()["error"].get("description", "Unknown")
                logger.error("\033[0;31m" + msg + "\033[0m")
                sys.exit(r.status_code)

    def delete(self, repo_id=None):
        """
        Deletes a repository. When a repository is deleted, it is removed from
        the database and its local working directory is deleted. The content
        within the repository, however, is not deleted. Deleting content is
        handled through the orphaned unit process.

        Deleting a repository is performed in the following major steps:

        1) Delete the repository.
        2) Unbind all bound consumers.


        :param repo_id str: the repository id
        :param repo_id list: a list of repositories id
        :return: None

        """
        logger = logging.getLogger(__name__ + ".delete")

        # API request
        if repo_id is not None:
            r = requests.delete(
                self.url + repo_id + "/", auth=self.auth, verify=False,
                headers={"Content-Type": "application/json"}
            )

            # Error handlers
            if r.status_code == 202:
                tasks = [item["task_id"] for item in r.json()["spawned_tasks"]]
                msg = "Created deletion task(s): {0} for repository: {1}".format(
                    tasks, repo_id)
                logger.info(msg)
            elif r.status_code == 404:
                msg = "Repository [{0}] does not exist".format(repo_id)
                logger.error("\033[0;31m" + msg + "\033[0m")
                sys.exit(r.status_code)
