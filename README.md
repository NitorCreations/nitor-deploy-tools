# Nitor tools for cloud deployments

## Introduction

**nitor-deploy-tools** is a set of tools for infrastructure-as-code on Amazon Web Services.

nitor-deploy-tools works by defining _Amazon Machine Instances_ and
deploying _[CloudFormation](https://aws.amazon.com/cloudformation/)
stacks_ of resources.

To use nitor-deploy-tools you need to set up a _project repository_ that
describes the images you want to build, and the stacks
you want to deploy them in. See
[ndt-project-template](https://github.com/NitorCreations/ndt-project-template)
for an example.

## Installation

```
pip install nitor-deploy-tools
```

## Commands for getting started

All of these are run in your project repository root. You need to have AWS credentials for command line access set up.

* To bake a new version of an image: `bake-image.sh <image-name>`
* To deploy a stack:
  * with a known AMI id: `ndt deploy-stack <image-name> <stack-name> <AMI-id>`
  * with the newest AMI id by a given bake job: `ndt deploy-stack <image-name> <stack-name> "" <bake-job-name>`
* To undeploy a stack: `ndt undeploy-stack <image-name> <stack-name>`

## Utilities for Lastpass integration

TODO

## Vault

A class and a command line utility to store secrets with client side encryption
