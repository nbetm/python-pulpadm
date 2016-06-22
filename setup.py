import os
import sys
from shutil import copyfile
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from pulpadm.constants import PKG_NAME, PKG_DESC, BASE_DIR, TMPL_DIR


# Global variables
#
version = "0.1.1"
requires = [
    "future",
    "requests",
    "PyYAML"
]

# Python v2.6 does not include argparse on the stdlib
if sys.version_info[:2] == (2, 6):
    requires.append("argparse>=1.1")


def read(fname):
    """
    Utility function to read the README file (long_description)
    It's nice, because now:
      1) we have a top level README
      2) it's easier to type in the README than to put a raw string in below
    """
    data = ""
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as stream:
        data = stream.read()
    stream.closed
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
    long_description=read("README"),
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
