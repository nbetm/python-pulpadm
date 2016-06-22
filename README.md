# PulpAdm

### Table of Contents

 - [Description](#description)
 - [Installation](#installation)
  - [Configuration](#configuration)
 - [Usage](#usage)
 - [Limitations](#limitations)
 - [TODO](#TODO)

## Description

PulpAdm is a CLI tool that helps you manage your RPM repositories in a Pulp
Server (usually the master). It was initially developed with the idea of filling
the void of doing repetitive tasks around RPM repositories in the commonly known
`pulp-admin` that comes with Pulp.

Pulp is a platform for managing repositories of content, such as software
packages, and pushing that content out to large numbers of consumers. For more
information, check out the project [website][pulp-home].

*Notice: this application does not implement (I'm not trying to reinvent the
wheel here) a full admin interface for Pulp. If you are looking for a full admin
client interface, use `pulp-admin` instead.*

## Installation

Clone this repository and use `setup.py`:
```bash
git clone https://github.com/nbetm/python-pulpadm.git
cd pulpadm
python setup.py install
```

### Configuration

By default, PulpAdm stage its configuration file under `~/.pulpadm/` directory.
Here is where you configure the *hostname* and *credentials* of the Pulp Server.
A template of the configuration file can be found [here][config-tmpl].

## Usage

PulpAdm comes with a CLI Interface called: `pulpadm`. Use the `-h` flag to learn
more about it and what it can do.

A simple example could be when you deploy a new Pulp Infrastructure and a set of
repositories need to be created. In oder to do so, you just need to have a YAML
file with a list of repositories and their configuration data (Feed, Relative
URL, Enable HTTP... and so on); then use the `create` action (under the `repo`
section) and feed this file. A template of this data file can be found
[here][repos-tmpl].

## Limitations

So far the only limitation is that PulpAdm was developed using Pulp v2.8 RESTful
API.

## TODO

 - Be able to delete and update repositories (not just create) Create a chain of
 - repositories in order to create a *Release Workflow*. For example:
  - upstream -> unstable -> stable
  - upstream -> lab -> dev -> prod
 - Promote content units using the *Release Workflow* mentioned above
 - Bind repositories to child nodes

  [pulp-home]: <http://www.pulpproject.org/>
  [config-tmpl]: <pulpadm/templates/config.yaml>
  [repos-tmpl]: <pulpadm/templates/repos.yaml>
