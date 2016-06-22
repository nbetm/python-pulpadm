from __future__ import print_function, unicode_literals
from builtins import open
import os
import logging
import yaml


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
