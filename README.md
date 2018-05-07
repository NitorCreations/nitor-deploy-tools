# Nitor Deploy Tools

## Released version 1.0a24

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
usage: ndt account-id [-h]

Get current account id. Either from instance metadata or current cli
configuration.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt add-deployer-server`

```bash
usage: ndt add-deployer-server [-h] [--id ID] file username

Add a server into a maven configuration file. Password is taken from the
environment variable \'DEPLOYER_PASSWORD\'

positional arguments:
  file        The file to modify
  username    The username to access the server.

optional arguments:
  -h, --help  show this help message and exit
  --id ID     Optional id for the server. Default is deploy. One server with
              this id is added and another with \'-release\' appended
```

### `ndt assume-role`

```bash
usage: ndt assume-role [-h] [-t TOKEN_NAME] role_arn

Assume a defined role. Prints out environment variables to be eval\'d to
current context for use: eval $(ndt assume-role
\'arn:aws:iam::43243246645:role/DeployRole\')

positional arguments:
  role_arn              The ARN of the role to assume

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN_NAME, --mfa-token TOKEN_NAME
                        Name of MFA token to use
```

### `ndt bake-docker`

```bash
usage: ndt bake-docker [-h] [-i] component docker-name

Runs a docker build, ensures that an ecr repository with the docker name
(by default <component>/<branch>-<docker-name>) exists and pushes the built
image to that repository with the tags "latest" and "$BUILD_NUMBER"

positional arguments:
  component   the component directory where the docker directory is
  docker-name the name of the docker directory that has the Dockerfile
              For example for ecs-cluster/docker-cluster/Dockerfile
              you would give cluster

optional arguments:
  -h, --help  show this help message and exit
  -i, --imagedefinitions  create imagedefinitions.json for AWS CodePipeline
```

### `ndt bake-image`

```bash
usage: ndt bake-image [-h] component

Runs an ansible playbook that  builds an Amazon Machine Image (AMI) and
tags the image with the job name and build number.

positional arguments
  component   the component directory where the ami bake configurations are

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-delete-stack`

```bash
usage: ndt cf-delete-stack [-h] stack_name region

Delete an existing CloudFormation stack

positional arguments:
  stack_name  Name of the stack to delete
  region      The region to delete the stack from

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-follow-logs`

```bash
usage: ndt cf-follow-logs [-h] [-s START] stack_name

Tail logs from the log group of a cloudformation stack

positional arguments:
  stack_name            Name of the stack to watch logs for

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        Start time in seconds since epoc
```

### `ndt cf-get-parameter`

```bash
usage: ndt cf-get-parameter [-h] parameter

Get a parameter value from the stack

positional arguments:
  parameter   The name of the parameter to print

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-logical-id`

```bash
usage: ndt cf-logical-id [-h]

Get the logical id that is expecting a signal from this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-region`

```bash
usage: ndt cf-region [-h]

Get region of the stack that created this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-signal-status`

```bash
usage: ndt cf-signal-status [-h] [-r RESOURCE] status

Signal CloudFormation status to a logical resource in CloudFormation that is
either given on the command line or resolved from CloudFormation tags

positional arguments:
  status                Status to indicate: SUCCESS | FAILURE

optional arguments:
  -h, --help            show this help message and exit
  -r RESOURCE, --resource RESOURCE
                        Logical resource name to signal. Looked up from
                        cloudformation tags by default
```

### `ndt cf-stack-id`

```bash
usage: ndt cf-stack-id [-h]

Get id of the stack the creted this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-stack-name`

```bash
usage: ndt cf-stack-name [-h]

Get name of the stack that created this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt create-account`

```bash
usage: ndt create-account [-h] [-d] [-o ORGANIZATION_ROLE_NAME]
                          [-r TRUST_ROLE_NAME]
                          [-a [TRUSTED_ACCOUNTS [TRUSTED_ACCOUNTS ...]]]
                          [-t TOKEN_NAME]
                          email account_name

Creates a subaccount.

positional arguments:
  email                 Email for account root
  account_name          Organization unique account name

optional arguments:
  -h, --help            show this help message and exit
  -d, --deny-billing-access
  -o ORGANIZATION_ROLE_NAME, --organization-role-name ORGANIZATION_ROLE_NAME
                        Role name for admin access from parent account
  -r TRUST_ROLE_NAME, --trust-role-name TRUST_ROLE_NAME
                        Role name for admin access from parent account
  -a [TRUSTED_ACCOUNTS [TRUSTED_ACCOUNTS ...]], --trusted-accounts [TRUSTED_ACCOUNTS [TRUSTED_ACCOUNTS ...]]
                        Account to trust with user management
  -t TOKEN_NAME, --mfa-token TOKEN_NAME
                        Name of MFA token to use
```

### `ndt create-stack`

```bash
usage: ndt create-stack [-h] [-y] [template]

Create a stack from a template

positional arguments:
  template

optional arguments:
  -h, --help  show this help message and exit
  -y, --yes   Answer yes or use default to all questions
```

### `ndt deploy-serverless`

```bash
usage: ndt deploy-serverless [-d] [-h] component serverless-name

Exports ndt parameters into component/serverless-name/variables.yml, runs npm i in the
serverless project and runs sls deploy -s branch for the same

positional arguments:
  component   the component directory where the serverless directory is
  serverless-name the name of the serverless directory that has the template
                  For example for lambda/serverless-sender/template.yaml
                  you would give sender

optional arguments:
  -d, --dryrun  dry-run - do only parameter expansion and template pre-processing and npm i
  -h, --help    show this help message and exit
```

### `ndt deploy-stack`

```bash
ami that is tagged with the bake-job name
usage: ndt deploy-stack [-d] [-h] component stack-name ami-id bake-job

Resolves potential ECR urls and AMI Ids and then deploys the given stack either updating or creating it.
positional arguments:
  component   the component directory where the stack template is
  stack-name  the name of the stack directory inside the component directory
              For example for ecs-cluster/stack-cluster/template.yaml
              you would give cluster
  ami-id      If you want to specify a value for the paramAmi variable in the stack,
              you can do so. Otherwise give an empty string with two quotation marks
  bake-job    If an ami-id is not given, the ami id is resolved by getting the latest

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt detach-volume`

```bash
