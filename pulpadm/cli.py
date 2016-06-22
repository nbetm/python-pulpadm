from __future__ import absolute_import, print_function
import argparse
import logging
import logging.config
import pkg_resources
import pulpadm.repo as repo
import pulpadm.utils as utils
from pulpadm.constants import PKG_NAME, PKG_DESC, CONFIG_FILE, LOG_LEVEL


def main():
    version = pkg_resources.get_distribution(PKG_NAME).version

    # Parent parser
    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument("--config", type=str, dest="config_file",
                               default=CONFIG_FILE,
                               help="""specifies alternative path of the config
                                    file""")
    parent_parser.add_argument("--hostname", type=str, dest="hostname",
                               default=None,
                               help="""specifies Pulp server hostname.
                                    supersedes the value on config file""")
    parent_parser.add_argument("--port", type=int, dest="port",
                               default=None,
                               help="""specifies Pulp server RESTful HTTP port.
                                    supersedes the value on config file""")
    parent_parser.add_argument("--username", type=str, dest="username",
                               default=None,
                               help="""specifies Pulp server account username.
                                    supersedes the value on config file""")
    parent_parser.add_argument("--password", type=str, dest="password",
                               default=None,
                               help="""specifies Pulp server account password.
                                    supersedes the value on config file""")
    parent_parser.add_argument('--log-level', type=str, dest='log_level',
                               choices=LOG_LEVEL,
                               default=LOG_LEVEL[2],
                               help='specifies console log level')

    # Top-level parser
    parser = argparse.ArgumentParser(
        prog=PKG_NAME,
        description=PKG_DESC,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-V", "--version", action="version",
                        version="{0} v{1}".format(PKG_NAME, version))

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
            description="Manage RPM repositories on the Pulp server",
            parents=[parent_parser]
    )
    repo_subparsers = section_repo_parser.add_subparsers(
        title="available actions",
        dest="action"
    )

    # Repo action parser: create
    repo_create_parser = repo_subparsers.add_parser(
        "create", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="creates RPM repositories from input file on the Pulp server",
        description="Creates RPM repositories from input file on the Pulp server",
        parents=[parent_parser]
    )
    repo_create_parser.add_argument(
        "path", type=str,
        help="""specifies the path of the input file in YAML format with the
             repositories and configuraiton data to be created"""
    )
    repo_create_parser.add_argument(
        "--repo-id", type=str, dest="repo_id",
        help="""if specified, RPM repo is created for one repository"""
    )
    repo_create_parser.set_defaults(func=repo.create)

    # Repo action parser: generate
    repo_generate_parser = repo_subparsers.add_parser(
        "generate", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="""generates JSON object from input file. The 'create' action uses
             the same internal process to generate the data for the RESTful API
             on the Pulp server""",
        description="""generates JSON object from input file. The 'create'
                    action uses the same internal process to generate the data
                    for the RESTful API on the Pulp server""",
        parents=[parent_parser]
    )
    repo_generate_parser.add_argument(
        "path", type=str,
        help="""specifies the path of the input file in YAML format with the
             repositories and configuraiton data to be created"""
    )
    repo_generate_parser.add_argument(
        "--repo-id", type=str, dest="repo_id",
        help="""if specified, JSON object is generated for one repository"""
    )
    repo_generate_parser.set_defaults(func=repo.create)

    # Repo action parser: list
    repo_list_parser = repo_subparsers.add_parser(
        "list", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="lists RPM repositories on the Pulp server",
        description="Lists RPM repositories on the Pulp server",
        parents=[parent_parser]
    )
    repo_list_parser.add_argument(
        "--repo-id", type=str, dest="repo_id",
        help="""if specified, configuration information is displayed for one
             repository"""
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
    repo_list_parser.set_defaults(func=repo.list)

    # Parse arguments
    args = parser.parse_args()

    # Setup root-level logger
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(levelname)-8s [%(name)s] %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console"
            }
        },
        "root": {
            "level": args.log_level.upper(),
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


if __name__ == "__main__":
    main()
