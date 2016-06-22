import os
import pkg_resources

PKG_NAME = "pulpadm"
PKG_DESC = "Pulp Admin Tool to Manage RPM Repositories"

BASE_DIR = os.path.expanduser(os.path.join("~", "." + PKG_NAME))
TMPL_DIR = pkg_resources.resource_filename(__name__, "templates")

CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")

LOG_LEVEL = ["critical", "error", "warning", "info", "debug"]

MAX_SPEED = 10485760

API_PATH = {
    "repositories": "/pulp/api/v2/repositories/"
}
