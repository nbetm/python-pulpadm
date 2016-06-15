from __future__ import print_function, unicode_literals
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
import pulpadm.utils as utils
from pulpadm.constants import API_PATH, MAX_SPEED


# Disable urllib3 warnings at the top-level
requests.packages.urllib3.disable_warnings()


def _generate_repo_create(id=None, config=None):
    """
    Generates a dict object to be used by the create repository end-point
    RESTful API

    :type id: str
    :param id: The repository id
    :type config: dict
    :param config: The repository config data
    """
    if id and config:
        return {
            "id": id,
            "display_name": config.get("display_name", None),
            "notes": {
                "_repo-type": "rpm-repo"
            },
            "importer_type_id": "yum_importer",
            "importer_config": {
                "feed": config.get("feed", None),
                "max_speed": MAX_SPEED if "feed" in config and "max_speed" not in config
                else config.get("max_speed", None),
                "feed": config.get("feed", None),
                "proxy_host": config.get("proxy_host", None),
                "proxy_port": config.get("proxy_port", None),
                "ssl_ca_cert": utils.read_file(config.get("feed_ca_cert", None)),
                "ssl_client_cert": utils.read_file(config.get("feed_cert", None)),
                "ssl_client_key": utils.read_file(config.get("feed_key", None))
            },
            "distributors": [
                {
                    "distributor_id": "yum_distributor",
                    "distributor_type_id": "yum_distributor",
                    "distributor_config": {
                        "http": config.get("serve_http", True),
                        "https": config.get("serve_https", True),
                        "relative_url": config.get("relative_url", None)
                    },
                    "auto_publish": True
                },
                {
                    "distributor_id": "export_distributor",
                    "distributor_type_id": "export_distributor",
                    "distributor_config": {
                        "http": config.get("serve_http", True),
                        "https": config.get("serve_https", True),
                        "relative_url": config.get("relative_url", None)
                    },
                    "auto_publish": False
                }
            ]
        }
    else:
        return {}


def create(args):
    """
    CLI wrapper function for aciton: crete and generate
    """
    logger = logging.getLogger(__name__ + '.create')

    # Read data from file and generate API JSON object
    data = utils.read_yaml(path=args.path)
    if data and type(data) is dict:
        for repo_id, repo_config in data.iteritems():
            if args.repo_id and args.repo_id != repo_id:
                continue

            # generate api data
            data_api = _generate_repo_create(id=repo_id, config=repo_config)

            # generate | create
            if args.action == "generate":
                print(json.dumps(data_api, indent=4, separators=(",", ": ")))
            elif args.action == "create":
                # API request
                url = "https://{0}:{1}{2}".format(args.hostname, args.port,
                                                  API_PATH["repositories"])
                r = requests.post(
                    url,
                    auth=HTTPBasicAuth(args.username, args.password),
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(data_api),
                    verify=False,
                )
                if r.status_code == 201:
                    logger.info("Created resource: {0}".format(repo_id))
                elif r.status_code == 409:
                    logger.warning(r.json()["error"].get("description", "Unknown"))
                else:
                    logger.error(r.json()["error"].get("description", "Unknown"))


def list(args):
    """
    CLI wrapper function for aciton: list
    """
    #  logger = logging.getLogger(__name__ + '.list')

    # API request
    url = "https://{0}:{1}{2}".format(args.hostname, args.port, API_PATH["repositories"])
    if args.repo_id:
        url += "{0}/".format(args.repo_id)
    r = requests.get(
        url,
        auth=HTTPBasicAuth(args.username, args.password),
        headers={"Content-Type": "application/json"},
        params={"details": args.details},
        verify=False,
    )
    data_api = [r.json()] if args.repo_id else r.json()

    # details | summary | simple
    if args.details:
        print(json.dumps(data_api, indent=4, separators=(",", ": ")))
    elif args.summary:
        for repo in data_api:
            print()
            print("{0:<22}{1}".format("Id:", repo["id"]))
            print("{0:<22}{1}".format("Display Name:", repo["display_name"]))
            print("Content Unit Counts:")
            if repo["content_unit_counts"]:
                for key, value in repo["content_unit_counts"].iteritems():
                    print("  {0:<18}{1}".format(key.replace("_", " ").title() + ":", value))
    else:
        for repo in data_api:
            print(repo["id"])
