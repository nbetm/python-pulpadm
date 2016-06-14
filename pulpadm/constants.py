import os

PKG_NAME = "pulpadm"

BASE_DIR = os.path.expanduser(os.path.join("~", "." + PKG_NAME))

CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")

LOG_LEVEL = ["critical", "error", "warning", "info", "debug"]

MAX_SPEED = 10485760

API_PATH = {
    "repositories": "/pulp/api/v2/repositories/"
}
