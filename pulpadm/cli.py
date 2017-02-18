from __future__ import absolute_import, print_function
import sys
import json
import argparse
import logging
import logging.config
import pkg_resources
import pulpadm.repo
import pulpadm.utils as utils
from pulpadm.constants import PKG_NAME, PKG_DESC, CONFIG_FILE


def repo_create_generate(args):
    """
    Wrapper function for action: Create & Generate
    """
    # Initiate RPMRepo object
    repo = pulpadm.repo.RPMRepo(hostname=args.hostname, port=args.port,
                                username=args.username, password=args.password)

    # Map CLI args and generate repo create object for end-point API
    repo_attrs = {
        "display_name": args.display_name,
        "feed": args.feed,
        "max_speed": args.max_speed,
        "relative_url": args.relative_url,
        "serve_http": True if args.serve_http == "true" else False,
        "serve_https": True if args.serve_https == "true" else False,
        "feed_ca_cert": args.feed_ca_cert,
        "feed_cert": args.feed_cert,
        "feed_key": args.feed_key,
        "proxy_host": args.proxy_host,
        "proxy_port": args.proxy_port
    }
    data = repo.generate_repo_create(repo_id=args.repo_id, **repo_attrs)

    # Print object as JSON or send request to API (create)
    if args.action == "generate":
        print(json.dumps(data, indent=4, separators=(",", ": ")))
    elif args.action == "create":
        repo.create(repo_config=data)


def repo_delete(args):
    """
    Wrapper function for action: Delete
    """
    # Initiate RPMRepo object
    repo = pulpadm.repo.RPMRepo(hostname=args.hostname, port=args.port,
                                username=args.username, password=args.password)

    # Delete repo(s)
    for item in args.repo_id:
        repo.delete(repo_id=item)


def repo_import(args):
    """
    Wrapper function for action: Import
    """
    # Initiate RPMRepo object
    repo = pulpadm.repo.RPMRepo(hostname=args.hostname, port=args.port,
                                username=args.username, password=args.password)

    # Read data from file
    data_yaml = utils.read_yaml(path=args.path)
    data_to_print = []

    # Iterate thru list of repos
    for repo_id, repo_attrs in data_yaml.iteritems():
        # Bypass repo_id when filtering
        if args.repo_id and repo_id not in args.repo_id:
            continue

        # Generate repo create object for end-point API
        data = repo.generate_repo_create(repo_id=repo_id, **repo_attrs)
        if args.generate:
            data_to_print.append(data)
        else:
            repo.create(repo_config=data)

    # Print object as JSON or send request to API (create)
    if args.generate:
        print(json.dumps(data_to_print, indent=4, separators=(",", ": ")))


def repo_list(args):
    """
    Wrapper function for action: List
    """
    # Initiate RPMRepo object
    repo = pulpadm.repo.RPMRepo(hostname=args.hostname, port=args.port,
                                username=args.username, password=args.password)

    # Get repo(s) and information
    data = repo.get(repo_id=args.repo_id, details=args.details)

    # Print data => details | summary | simple
    if args.details:
        print(json.dumps(data, indent=4, separators=(",", ": ")))
    elif args.summary:
        for item in data:
            print()
            print("{0:<22}{1}".format("Id:", item["id"]))
            print("{0:<22}{1}".format("Display Name:", item["display_name"]))
            print("Content Unit Counts:")
            if item["content_unit_counts"]:
                for key, value in item["content_unit_counts"].iteritems():
                    print("  {0}{1}".format(key.replace("_", " ").title() + ": ", value))
    else:
        for item in data:
            print(item["id"])


def main():
    version = pkg_resources.get_distribution(PKG_NAME).version

    # Top-level parser
    parser = argparse.ArgumentParser(
        prog=PKG_NAME,
        description=PKG_DESC,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config", type=str, dest="config_file", default=CONFIG_FILE, metavar="",
        help="""full path of an alternative config file"""
    )
    parser.add_argument(
        "--hostname", type=str, dest="hostname", default=None, metavar="",
        help="""Pulp server hostname (supersedes config file value)"""
    )
    parser.add_argument(
        "--port", type=int, dest="port", default=None, metavar="",
        help="""Pulp server RESTful HTTP port (supersedes config file value)"""
    )
    parser.add_argument(
        "--username", type=str, dest="username", default=None, metavar="",
        help="""Pulp server account username (supersedes config file value)"""
    )
    parser.add_argument(
        "--password", type=str, dest="password", default=None, metavar="",
        help="""Pulp server account password (supersedes config file value)"""
    )
    parser.add_argument(
        "-v", dest="verbose", action="count", default=0,
        help="""increases output verbosity (-v for INFO & -vv for DEBUG)"""
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version="{0} v{1}".format(PKG_NAME, version)
    )

    # Section subparsers
    #
    section_subparsers = parser.add_subparsers(
        title="available sections",
        dest="section"
    )
    section_subparsers.required = True

    # Repo Section & Action parsers
    #
    section_repo_parser = section_subparsers.add_parser(
        "repo",
        help="manage RPM repositories on the Pulp server",
        description="Manage RPM repositories on the Pulp server"
    )
    repo_subparsers = section_repo_parser.add_subparsers(
        title="available actions",
        dest="action"
    )
    repo_create_generate_update_parser = argparse.ArgumentParser(add_help=False)
    repo_create_generate_update_parser.add_argument(
        "repo_id", type=str, metavar="",
        help="""unique identifier; only alphanumeric, ., -, and _ allowed"""
    )
    repo_create_generate_update_parser.add_argument(
        "--display-name", dest="display_name", type=str, metavar="",
        help="""user-readable display name (i18n characters)"""
    )
    repo_create_generate_update_parser.add_argument(
        "--feed", dest="feed", type=str, metavar="",
        help="""URL of the external source repository to sync"""
    )
    repo_create_generate_update_parser.add_argument(
        "--max-speed", dest="max_speed", type=int, metavar="",
        help="""maximum bandwidth used per download thread (bytes/sec), when
        synchronizing the repo (default: 10485760 ***if feed URL)"""
    )
    repo_create_generate_update_parser.add_argument(
        "--relative-url", dest="relative_url", type=str, metavar="",
        help="""relative path the repository will be served from. Only
        alphanumeric characters, forward slashes, underscores and dashes
        are allowed (default: relative path of the feed URL)"""
    )
    repo_create_generate_update_parser.add_argument(
        "--serve-http", dest="serve_http", type=str, choices=["true", "false"],
        default="true", metavar="",
        help="""if "true", the repository will be served over HTTP
        (default: true)"""
    )
    repo_create_generate_update_parser.add_argument(
        "--serve-https", dest="serve_https", type=str, choices=["true", "false"],
        default="true", metavar="",
        help="""if "true", the repository will be served over HTTPS
        (default: true)"""
    )
    repo_create_generate_update_parser.add_argument(
        "--feed-ca-cert", dest="feed_ca_cert", type=str, metavar="",
        help="""full path to the CA certificate that should be used to verify
        the external repo server's SSL certificate"""
    )
    repo_create_generate_update_parser.add_argument(
        "--feed-cert", dest="feed_cert", type=str, metavar="",
        help="""full path to the certificate to use for authorization when
             accessing the external feed"""
    )
    repo_create_generate_update_parser.add_argument(
        "--feed-key", dest="feed_key", type=str, metavar="",
        help="""full path to the private key for feed_cert"""
    )
    repo_create_generate_update_parser.add_argument(
        "--proxy-host", dest="proxy_host", type=str, metavar="",
        help="""proxy server url to use"""
    )
    repo_create_generate_update_parser.add_argument(
        "--proxy-port", dest="proxy_port", type=str, metavar="",
        help="""port on the proxy server to make requests"""
    )

    # Repo action parser: create
    repo_create_parser = repo_subparsers.add_parser(
        "create",
        help="creates RPM repository on the Pulp server",
        description="Creates RPM repository on the Pulp server",
        parents=[repo_create_generate_update_parser]
    )
    repo_create_parser.set_defaults(func=repo_create_generate)

    # Repo action parser: delete
    repo_delete_parser = repo_subparsers.add_parser(
        "delete",
        help="deletes RPM repository on the Pulp server",
        description="Deletes RPM repository on the Pulp server"
    )
    repo_delete_parser.add_argument(
        "repo_id", nargs="+", type=str,
        help="""specifies the repo id to be deleted (multiple entries must be
        separated by space)"""
    )
    repo_delete_parser.set_defaults(func=repo_delete)

    #  Repo action parser: generate
    repo_generate_parser = repo_subparsers.add_parser(
        "generate",
        help="""generates create repository API object (JSON)""",
        description="""Generates create repository API object (JSON)""",
        parents=[repo_create_generate_update_parser]
    )
    repo_generate_parser.set_defaults(func=repo_create_generate)

    #  Repo action parser: import
    repo_import_parser = repo_subparsers.add_parser(
        "import",
        help="""same as create, but from input file""",
        description="""Same as create, but from input file instead. Very useful
        when creating a set of repositories. See `~/.pulpadm/repos.yaml' for an
        example of the input file."""
    )
    repo_import_parser.add_argument(
        "path", type=str,
        help="""specifies the full path of the input file"""
    )
    repo_import_parser.add_argument(
        "--repo-id", nargs="+", type=str, dest="repo_id", metavar="",
        help="""if specified, the given repository is created (multiple entries
        must be separated by space)"""
    )
    repo_import_parser.add_argument(
        "--generate", action="store_true",
        help="""returns the create repository API object instead of create"""
    )
    repo_import_parser.set_defaults(func=repo_import)

    # Repo action parser: list
    repo_list_parser = repo_subparsers.add_parser(
        "list",
        help="lists RPM repositories on the Pulp server",
        description="Lists RPM repositories on the Pulp server"
    )
    repo_list_parser.add_argument(
        "--repo-id", type=str, dest="repo_id", metavar="",
        help="""if specified, configuration information is displayed for the
        given repository"""
    )
    repo_list_parser_group = repo_list_parser.add_mutually_exclusive_group()
    repo_list_parser_group.add_argument(
        "--details", action="store_true",
        help="""if specified, detailed configuration information is displayed in
        JSON format for each repository"""
    )
    repo_list_parser_group.add_argument(
        "--summary", action="store_true",
        help="""if specified, a condensed view for each repository will be
        displayed instead"""
    )
    repo_list_parser.set_defaults(func=repo_list)

    # Parse arguments
    args = parser.parse_args()

    # Define Log Level
    if args.verbose >= 2:
        log_level = "DEBUG"
        log_format = "%(levelname)s [%(name)s] %(message)s"
    elif args.verbose >= 1:
        log_level = "INFO"
        log_format = "%(message)s"
    else:
        log_level = "WARNING"
        log_format = "%(message)s"

    # Setup root-level logger
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False if log_level == "DEBUG" else True,
        "formatters": {
            "console": {
                "format": log_format
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    })

    # Re-generate Pulp Server Info
    #   CLI Args supersedes the values from the CONFIG_FILE
    #
    c_all = utils.read_yaml(args.config_file)
    c = c_all.get("pulp_server", {}) if type(c_all) is dict else {}
    args.hostname = args.hostname if args.hostname else c.get("hostname", None)
    args.port = args.port if args.port else c.get("port", None)
    args.username = args.username if args.username else c.get("username", None)
    args.password = args.password if args.password else c.get("password", None)

    # Call sub-command functions
    args.func(args)

    # Exit
    sys.exit(0)


if __name__ == "__main__":
    main()
