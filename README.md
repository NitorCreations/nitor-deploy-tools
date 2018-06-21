# Nitor Deploy Tools
[![Build Status](https://travis-ci.org/NitorCreations/nitor-deploy-tools.svg?branch=master)](https://travis-ci.org/NitorCreations/nitor-deploy-tools)
[![Coverage Status](https://coveralls.io/repos/github/NitorCreations/nitor-deploy-tools/badge.svg?branch=master)](https://coveralls.io/github/NitorCreations/nitor-deploy-tools?branch=master)

## Released version 1.0a33

Nitor deploy tools are a set of tools to implement a true Infrastructure As Code workflow
with AWS and CloudFormation.

## Rationale

We at Nitor are software engineers with mostly a developer or architect background, but
a lot of us have had to work closely with various Operations teams around the world.
DevOps has a natural appeal to us and immediately "infrastructure as code" meant for us
that we should apply the best development practices to infrastructure development. It starts
with version control and continues with testing new features in isolation and a workflow
that supports this. Our teams usually take into use a feature branch workflow if it is
feasible and we expect all of the tools and practices to support this. For infrastructure
this type of branching means that you should be able to spin up enough of the infrastructure
to be able to verify the changes you want to implement in production. Also the testing
environment should be close enough to the target environment for the results to be valid.
So the differences between testing and production environments should be minimized and
reviewable.

With the popular tools like Ansible, Terraform, Chef etc. you need to come up with and
implement the ways to achieve the goals above. As far as I know, no tool besides ndt
has at it's core a thought-out way of a branching infrastructure development model.

## What it is

nitor-deploy-tools works by defining _Amazon Machine Images_, _Docker containers_ and
deploying _[CloudFormation](https://aws.amazon.com/cloudformation/) stacks_ of resources.

To use nitor-deploy-tools you need to set up a _project repository_ that
describes the images you want to build, and the stacks you want to deploy them in. See
[ndt-project-template](https://github.com/NitorCreations/ndt-project-template)
for an example.

## Installation

```
pip install nitor-deploy-tools
```
On OSX you may need to add `--ignore-installed` to get around platform installed versions
of `six` and other packages.

## Commands for getting started

All of these are run in your project repository root. You need to have AWS credentials for
command line access set up.

* To bake a new version of an image: `ndt bake-image <image-name>`
* To build a new Docker container image `ndt bake-docker <component> <docker-name>`
* To deploy a stack:
  * with a known AMI id: `ndt deploy-stack <image-name> <stack-name> <AMI-id>`
  * with the newest AMI id by a given bake job: `ndt deploy-stack <image-name> <stack-name> "" <bake-job-name>`
* To undeploy a stack: `ndt undeploy-stack <image-name> <stack-name>`

## Command completion

Most things have decent bash command completion, even for things like AMI Ids in AWS. To make it work, the things
outputted by `nitor-dt-register-complete` need to be in your environment. So put the following somewhere
(e.g. your ~/.bashrc) where it gets run for your profile (or run it manually when working with ndt)
```bash
eval "$(nitor-dt-register-complete)"
```

## Commands

### `ndt account-id`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt add-deployer-server`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt assume-role`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt bake-docker`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt bake-image`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-delete-stack`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-follow-logs`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-get-parameter`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-logical-id`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-region`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-signal-status`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-stack-id`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt cf-stack-name`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt create-account`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt create-stack`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt deploy-serverless`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt deploy-stack`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt detach-volume`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ec2-clean-snapshots`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ec2-get-tag`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ec2-get-userdata`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ec2-instance-id`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ec2-region`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ecr-ensure-repo`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt ecr-repo-uri`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt get-images`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt interpolate-file`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt json-to-yaml`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt latest-snapshot`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt list-file-to-json`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt list-jobs`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt load-parameters`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt logs`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt mfa-add-token`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt mfa-backup`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt mfa-code`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt mfa-delete-token`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt print-create-instructions`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt promote-image`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt pytail`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt region`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt register-private-dns`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt setup-cli`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt share-to-another-region`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt show-stack-params-and-outputs`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt snapshot-from-volume`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt undeploy-stack`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt upsert-cloudfront-records`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt volume-from-snapshot`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt yaml-to-json`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `ndt yaml-to-yaml`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ndt", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]associate-eip`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/associate-eip", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]cf-logs-to-cloudwatch`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/cf-logs-to-cloudwatch", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]ec2-associate-eip`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/ec2-associate-eip", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]logs-to-cloudwatch`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/logs-to-cloudwatch", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]n-include`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/n-include", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]n-include-all`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/n-include-all", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `[ndt ]signal-cf-status`

```bash
Traceback (most recent call last):
  File "/usr/local/bin/signal-cf-status", line 6, in <module>
    from pkg_resources import load_entry_point
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3088, in <module>
    @_call_aside
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3072, in _call_aside
    f(*args, **kwargs)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3101, in _initialize_master_working_set
    working_set = WorkingSet._build_master()
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 574, in _build_master
    ws.require(__requires__)
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 892, in require
    needed = self.resolve(parse_requirements(requirements))
  File "/usr/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 778, in resolve
    raise DistributionNotFound(req, requirers)
pkg_resources.DistributionNotFound: The \'nitor-deploy-tools\' distribution was not found and is required by the application
```

### `create-shell-archive.sh`

```bash
file  one or more files to package into the archive
usage: create-shell-archive.sh [-h] [<file> ...]

Creates a self-extracting bash archive, suitable for storing in e.g. Lastpass SecureNotes
positional arguments:

optional arguments:
  -h, --help  show this help message and exit
```

### `encrypt-and-mount.sh`

```bash
Mounts a local block device as an encrypted volume. Handy for things like local database installs.
usage: encrypt-and-mount.sh [-h] blk-device mount-path


positional arguments
  blk-device  the block device you want to encrypt and mount
  mount-path  the mount point for the encrypted volume

optional arguments:
  -h, --help  show this help message and exit
```

### `ensure-letsencrypt-certs.sh`

```bash
usage: ensure-letsencrypt-certs.sh [-h] domain-name [domain-name ...]

Fetches a certificate with fetch-secrets.sh, and exits cleanly if certificate is found and valid.
Otherwise gets a new certificate from letsencrypt via DNS verification using Route53.
Requires that fetch-secrets.sh and Route53 are set up correctly.

positional arguments
  domain-name   The domain(s) you want to check certificates for

optional arguments:
  -h, --help  show this help message and exit
/usr/local/bin/ensure-letsencrypt-certs.sh: line 23: fetch-secrets.sh: command not found
```

### `lastpass-fetch-notes.sh`

```bash
--optional  marks that following files will not fail and exit the script in they do not exist
usage: lasptass-fetch-notes.sh [-h] mode file [file ...] [--optional file ...]

Fetches secure notes from lastpass that match the basename of each listed file.
Files specified after --optional won\'t fail if the file does not exist.

positional arguments
  mode   the file mode for the downloaded files
  file   the file(s) to download. The source will be the note that matches the basename of the file

optional arguments:
  -h, --help  show this help message and exit
```

### `lpssh`

```bash
usage: lpssh [-h] [-k key-name] user@example.com

Fetches key mappings from lastpass, downloads mapped keys into a local ssh-agent and starts
an ssh session using those credentials.

positional arguments
  user@example.com   The user and host to match in "my-ssh-mappings" secure note
                     and to log into once keys are set up.

optional arguments:
  -k,         key name in lastpass to use if you don\'t want to use a mapping
  -h, --help  show this help message and exit
```

### `setup-fetch-secrets.sh`

```bash
Please run as root
usage: setup-fetch-secrets.sh [-h] <lpass|s3|vault>

Sets up a global fetch-secrets.sh that fetches secrets from either LastPass, S3 or nitor-vault

positional arguments
  lpass|s3|vault   the selected secrets backend.

optional arguments:
  -h, --help  show this help message and exit exit 1
```

### `ssh-hostkeys-collect.sh`

```bash
usage: ssh-hostkeys-collect.sh [-h] hostname

Creates a <hostname>-ssh-hostkeys.sh archive in the current directory containing
ssh host keys to preserve the identity of a server over image upgrades.

positional arguments
  hostname   the name of the host used to store the keys. Typically the hostname is what
             instance userdata scripts will use to look for the keys

optional arguments:
  -h, --help  show this help message and exit
```

