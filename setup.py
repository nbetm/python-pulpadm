import os
import sys
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from pulpadm.utils import initial_setup, read_file as read
from pulpadm.constants import PKG_NAME, PKG_DESC


# Global variables
#
version = "0.1.0"
requires = [
    "future",
    "requests",
    "PyYAML"
]

# Python v2.6 does not include argparse on the stdlib
if sys.version_info[:2] == (2, 6):
    requires.append("argparse>=1.1")


class PostDevelopCommand(develop):
    """
    Post-installation for development mode
    """
    def run(self):
        initial_setup()
        develop.run(self)


class PostInstallCommand(install):
    """
    Post-installation for install mode
    """
    def run(self):
        initial_setup()
        install.run(self)


setup(
    name=PKG_NAME,
    description=PKG_DESC,
    long_description=read(os.path.join(os.path.dirname(__file__), "README")),
    version=version,
    author="Nelson R Monserrate",
    author_email="nrmonserrate@gmail.com",
    url="https://github.com/nbetm/python-pulpadm",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pulpadm = pulpadm.cli:main"]
    },
    cmdclass={
        "develop": PostDevelopCommand,
        "install": PostInstallCommand
    },
    include_package_data=True,
    package_data={
        "": ["templates/*"]
    },
    install_requires=requires,
    zip_safe=False,
)
