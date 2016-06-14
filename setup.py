import os
import sys
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = "0.1.0"
requires = [
    "future",
    "requests",
    "PyYAML",
    "tabulate"
]

# For python v2.6 we have to require argparse because is not part of stdlib
if sys.version_info[:2] == (2, 6):
    requires.append("argparse>=1.1")

setup(
    name="pulpadm",
    version=version,
    description="Pulp Admin Tool",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["pulpadm = pulpadm.cli:main"]
    },
    install_requires=requires,
    include_package_data=True,
    zip_safe=False,
    long_description=read("README"),
)
