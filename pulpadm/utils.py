from __future__ import print_function, unicode_literals
from builtins import open
import os
import logging
import yaml
from shutil import copyfile
from pulpadm.constants import BASE_DIR, TMPL_DIR


def read_yaml(path=None):
    """
    Reads a given file in YAML format and returns data as a Python object

    :type path: str
    :param path: The absolute path of the YAML file
    """
    logger = logging.getLogger(__name__ + '.read_yaml')

    data = None
    try:
        if path:
            with open(os.path.expanduser(path), 'r') as stream:
                data = yaml.load(stream)
            stream.closed
    except IOError as e:
        logger.error(e)
    except yaml.YAMLError as e:
        logger.error(e)
    finally:
        return data


def read_file(path=None):
    """
    Reads a given plain-text file and returns data as string

    :type path: str
    :param path: The absolute path of the file
    """
    logger = logging.getLogger(__name__ + '.read_file')

    data = None
    try:
        if path:
            with open(os.path.expanduser(path), 'r') as stream:
                data = stream.read()
            stream.closed
    except IOError as e:
        logger.error(e)
    finally:
        return data


def initial_setup():
    """
    Setup BASE_DIR and example files
    """
    print()
    if not os.path.exists(BASE_DIR):
        print("Creating {0}".format(BASE_DIR))
        os.mkdir(BASE_DIR)

    for fname in ["config.yaml", "repos.yaml"]:
        src = os.path.join(TMPL_DIR, fname)
        dst = os.path.join(BASE_DIR, fname)
        if os.path.exists(dst):
            dst += ".new"
        print("Copying {0} -> {1}".format(os.path.basename(src), dst))
        copyfile(src, dst)
    print()
