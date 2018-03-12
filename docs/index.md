# Nitor Deploy Tools

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

nitor-deploy-tools works by defining _Amazon Machine Instances_, _Docker containers_ and
deploying _[CloudFormation](https://aws.amazon.com/cloudformation/) stacks_ of resources.

To use nitor-deploy-tools you need to set up a _project repository_ that
describes the images you want to build, and the stacks you want to deploy them in. See
[ndt-project-template](https://github.com/NitorCreations/ndt-project-template)
for an example.

## Installation

```
pip install nitor-deploy-tools
```

## Commands for getting started

All of these are run in your project repository root. You need to have AWS credentials for command line access set up.

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

### `ndt ec2-associate-eip`

```bash
usage: ndt ec2-associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
                             [-p ALLOCATIONIDPARAM]

Associate an Elastic IP for the instance

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        Elastic IP to allocate - default is to get paramEip
                        from stack
  -a ALLOCATIONID, --allocationid ALLOCATIONID
                        Elastic IP allocation id to allocate - default is to
                        get paramEipAllocationId from stack
  -e EIPPARAM, --eipparam EIPPARAM
                        Parameter to look up for Elastic IP in the stack -
                        default is paramEip
  -p ALLOCATIONIDPARAM, --allocationidparam ALLOCATIONIDPARAM
                        Parameter to look up for Elastic IP Allocation ID in
                        the stack - default is paramEipAllocationId
```

### `ndt logs-to-cloudwatch`

```bash
usage: ndt logs-to-cloudwatch [-h] file

Read a file and send rows to cloudwatch and keep following the end for new
data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt latest-snapshot`

```bash
usage: ndt latest-snapshot [-h] tag

Get the latest snapshot with a given tag

positional arguments:
  tag         The tag to find snapshots with

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

### `ndt signal-cf-status`

```bash
usage: ndt signal-cf-status [-h] [-r RESOURCE] status

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

### `ndt share-to-another-region`

```bash
usage: ndt share-to-another-region [-h]
                                   ami_id to_region ami_name account_id
                                   [account_id ...]

Shares an image to another region for potentially another account

positional arguments:
  ami_id      The ami to share
  to_region   The region to share to
  ami_name    The name for the ami
  account_id  The account ids to share ami to

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt list-jobs`

```bash
fatal: Not a valid object name
```

### `ndt pytail`

```bash
usage: ndt pytail [-h] file

Read and print a file and keep following the end for new data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt ec2-region`

```bash
eu-west-1
```

### `ndt mfa-code`

```bash
usage: ndt mfa-code [-h] token_name

Generates a TOTP code using an MFA token.

positional arguments:
  token_name  Name of the token to use.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt upsert-cloudfront-records`

```bash
usage: ndt upsert-cloudfront-records [-h]
                                     (-i DISTRIBUTION_ID | -c DISTRIBUTION_COMMENT)
                                     [-w]

Upsert Route53 records for all aliases of a CloudFront distribution

optional arguments:
  -h, --help            show this help message and exit
  -i DISTRIBUTION_ID, --distribution_id DISTRIBUTION_ID
                        Id for the distribution to upsert
  -c DISTRIBUTION_COMMENT, --distribution_comment DISTRIBUTION_COMMENT
                        Comment for the distribution to upsert
  -w, --wait            Wait for request to sync
```

### `ndt ec2-get-userdata`

```bash
usage: ndt ec2-get-userdata [-h] file

Get userdata defined for an instance into a file

positional arguments:
  file        File to write userdata into

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt associate-eip`

```bash
usage: ndt associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
                         [-p ALLOCATIONIDPARAM]

Associate an Elastic IP for the instance

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        Elastic IP to allocate - default is to get paramEip
                        from stack
  -a ALLOCATIONID, --allocationid ALLOCATIONID
                        Elastic IP allocation id to allocate - default is to
                        get paramEipAllocationId from stack
  -e EIPPARAM, --eipparam EIPPARAM
                        Parameter to look up for Elastic IP in the stack -
                        default is paramEip
  -p ALLOCATIONIDPARAM, --allocationidparam ALLOCATIONIDPARAM
                        Parameter to look up for Elastic IP Allocation ID in
                        the stack - default is paramEipAllocationId
```

### `lpssh`

```bash
usage: lpssh [-k key-name] user@example.com

Fetches key mappings from lastpass, downloads mapped keys into a local ssh-agent and starts
an ssh session using those credentials.
```

### `ndt json-to-yaml`

```bash
usage: ndt json-to-yaml [-h] [--colorize] file

Convert CloudFormation json to an approximation of a Nitor CloudFormation yaml
with for example scripts externalized

positional arguments:
  file            File to parse

optional arguments:
  -h, --help      show this help message and exit
  --colorize, -c  Colorize output
```

### `ndt n-utils-init`

```bash

```

### `ndt deploy-stack`

```bash
usage: ndt deploy-stack <component> <stack-name> <ami-id or empty string> <bake job name for searching ami-id>

Resolves potential ECR urls and AMI Ids and then deploys the given stack either updating or creating it.
```

### `ndt account-id`

```bash
usage: ndt account-id [-h]

Get current account id. Either from instance metadata or current cli
configuration.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt n-include`

```bash
usage: ndt n-include [-h] file

Find a file from the first of the defined include paths

positional arguments:
  file        The file to find

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

### `ndt list-file-to-json`

```bash
usage: ndt list-file-to-json [-h] arrayname file

Convert a file with an entry on each line to a json document with a single
element (name as argument) containg file rows as list.

positional arguments:
  arrayname   The name in the json object givento the array
  file        The file to parse

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt assume-role`

```bash
usage: ndt assume-role [-h] [-t TOKEN_NAME] role_arn

Assume a defined role. Prints out environment variables to be eval'd to
current context for use: eval $(ndt assume-role
'arn:aws:iam::43243246645:role/DeployRole')

positional arguments:
  role_arn              The ARN of the role to assume

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN_NAME, --mfa-token TOKEN_NAME
                        Name of MFA token to use
```

### `ndt detach-volume`

```bash
usage: ndt detach-volume [-h] mount_path

Create a snapshot of a volume identified by it's mount path

positional arguments:
  mount_path  Where to mount the volume

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt encrypt-and-mount`

```bash
'-h' not a block device
Usage: /usr/bin/encrypt-and-mount.sh blk-device mount-path
```

### `ndt ecr-ensure-repo`

```bash
usage: ndt ecr-ensure-repo [-h] name

Ensure that an ECR repository exists and get the uri and login token for it

positional arguments:
  name        The name of the ecr repository to verify

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt n-include-all`

```bash
usage: ndt n-include-all [-h] pattern

Find a file from the first of the defined include paths

positional arguments:
  pattern     The file pattern to find

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt show-stack-params-and-outputs`

```bash
usage: ndt show-stack-params-and-outputs [-h] [-r REGION] [-p PARAMETER]
                                         stack_name

Show stack parameters and outputs as a single json documents

positional arguments:
  stack_name            The stack name to show

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        Region for the stack to show
  -p PARAMETER, --parameter PARAMETER
                        Name of paremeter if only one parameter required
```

### `ndt ec2-get-tag`

```bash
usage: ndt ec2-get-tag [-h] name

Get the value of a tag for an ec2 instance

positional arguments:
  name        The name of the tag to get

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt cf-delete-stack`

```bash
usage: ndt cf-delete-stack [-h] stack_name region

Create or update existing CloudFormation stack

positional arguments:
  stack_name  Name of the stack to delete
  region      The region to delete the stack from

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt ecr-repo-uri`

```bash
usage: ndt ecr-repo-uri [-h] name

Ensure that an ECR repository exists and get the uri and login token for it

positional arguments:
  name        The name of the ecr repository

optional arguments:
  -h, --help  show this help message and exit
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

### `ndt ec2-clean-snapshots`

```bash
usage: ndt ec2-clean-snapshots [-h] [-r REGION] [-d DAYS] tags [tags ...]

Clean snapshots that are older than a number of days (30 by default) and have
one of specified tag values

positional arguments:
  tags                  The tag values to select deleted snapshots

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        The region to delete snapshots from. Can also be set
                        with env variable AWS_DEFAULT_REGION or is gotten from
                        instance metadata as a last resort
  -d DAYS, --days DAYS  The number of days that is theminimum age for
                        snapshots to be deleted
```

### `ndt cf-logs-to-cloudwatch`

```bash
usage: ndt cf-logs-to-cloudwatch [-h] file

Read a file and send rows to cloudwatch and keep following the end for new
data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt bake-docker`

```bash
usage: ndt bake-docker <component> <docker-name>

Runs a docker build, ensures that an ecr repository with the docker name
(by default <component>/<branch>-<docker-name>) exists and pushes the built
image to that repository with the tags "latest" and "$BUILD_NUMBER"
```

### `ndt cf-logical-id`

```bash
usage: ndt cf-logical-id [-h]

Get the logical id that is expecting a signal from this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt lastpass-fetch-notes`

```bash

```

### `ndt ensure-letsencrypt-certs`

```bash
Please enter the LastPass master password for <webmaster@nitorcreations.com>.

Master Password: Error: Failed to enter correct password.
Error: Not currently logged in.
chmod: cannot access '/etc/certs/-h.crt': No such file or directory
+ CF_paramSecretsUser=webmaster@nitorcreations.com
+ case "$1" in
+ shift
+ mode=444
+ shift
+ login_if_not_already
+ lpass ls not-meant-to-return-anything
+ cat /home/pasi/.lpass/webmaster.pwd
+ lastpass-login.sh webmaster@nitorcreations.com -
cat: /home/pasi/.lpass/webmaster.pwd: No such file or directory
/usr/bin/ensure-letsencrypt-certs.sh: line 33: /etc/certs/conf: No such file or directory
ERROR: Invalid argument: -h
+ CF_paramSecretsUser=webmaster@nitorcreations.com
+ case "$1" in
+ shift
+ lastpass-logout.sh
```

### `ndt register-private-dns`

```bash
usage: ndt register-private-dns [-h] dns_name hosted_zone

Register local private IP in route53 hosted zone usually for internal use.

positional arguments:
  dns_name     The name to update in route 53
  hosted_zone  The name of the hosted zone to update

optional arguments:
  -h, --help   show this help message and exit
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

### `ndt mfa-add-token`

```bash
usage: ndt mfa-add-token [-h] [-i] [-a TOKEN_ARN] [-s TOKEN_SECRET] [-f]
                         token_name

Adds an MFA token to be used with role assumption. Tokens will be saved in a
.ndt subdirectory in the user's home directory. If a token with the same name
already exists, it will not be overwritten.

positional arguments:
  token_name            Name for the token. Use this to refer to the token
                        later with the assume-role command.

optional arguments:
  -h, --help            show this help message and exit
  -i, --interactive     Ask for token details interactively.
  -a TOKEN_ARN, --token_arn TOKEN_ARN
                        ARN identifier for the token.
  -s TOKEN_SECRET, --token_secret TOKEN_SECRET
                        Token secret.
  -f, --force           Force an overwrite if the token already exists.
```

### `ndt create-stack`

```bash
usage: ndt create-stack [-y] [-h] template
ndt create-stack: error: too few arguments
```

### `ndt snapshot-from-volume`

```bash
usage: ndt snapshot-from-volume [-h] [-w] tag_key tag_value mount_path

Create a snapshot of a volume identified by it's mount path

positional arguments:
  tag_key     Key of the tag to find volume with
  tag_value   Value of the tag to find volume with
  mount_path  Where to mount the volume

optional arguments:
  -h, --help  show this help message and exit
  -w, --wait  Wait for the snapshot to finish before returning
```

### `ndt bake-image`

```bash
usage: ndt bake-images <component>

Runs an ansible playbook that  builds an Amazon Machine Image (AMI) and
tags the image with the job name and build number.
```

### `ndt setup-fetch-secrets`

```bash
usage: setup-fetch-secrets.sh <lpass|s3|vault>

Sets up a global fetch-secrets.sh that fetches secrets from either LastPass, S3 or nitor-vault
```

### `ndt setup-cli`

```bash
usage: ndt setup-cli [-h] [-n NAME] [-k KEY_ID] [-s SECRET] [-r REGION]

Setup the command line environment to define an aws cli profile with the given
name and credentials. If an identically named profile exists, it will not be
overwritten.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name for the profile to create
  -k KEY_ID, --key-id KEY_ID
                        Key id for the profile
  -s SECRET, --secret SECRET
                        Secret to set for the profile
  -r REGION, --region REGION
                        Default region for the profile
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
                        Start time in seconds sinceepoc
```

### `ndt get-images`

```bash
usage: ndt get-images [-h] job_name

Gets a list of images given a bake job name

positional arguments:
  job_name    The job name to look for

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt mfa-delete-token`

```bash
usage: ndt mfa-delete-token [-h] token_name

Deletes an MFA token file from the .ndt subdirectory in the user's home
directory

positional arguments:
  token_name  Name of the token to delete.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt promote-image`

```bash
usage: ndt promote-image [-h] image_id target_job

Promotes an image for use in another branch

positional arguments:
  image_id    The image to promote
  target_job  The job name to promote the image to

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt volume-from-snapshot`

```bash
usage: ndt volume-from-snapshot [-h] [-n]
                                tag_key tag_value mount_path [size_gb]
ndt volume-from-snapshot: error: Only makes sense on an EC2 instance
```

### `ndt add-deployer-server`

```bash
usage: ndt add-deployer-server [-h] [--id ID] file username

Add a server into a maven configuration file. Password is taken from the
environment variable 'DEPLOYER_PASSWORD'

positional arguments:
  file        The file to modify
  username    The username to access the server.

optional arguments:
  -h, --help  show this help message and exit
  --id ID     Optional id for the server. Default is deploy. One server with
              this id is added and another with '-release' appended
```

### `ndt ec2-instance-id`

```bash
usage: ndt ec2-instance-id [-h]

Get id for instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt interpolate-file`

```bash
usage: ndt interpolate-file [-h] [-s STACK] [-v] [-o OUTPUT] [-e ENCODING]
                            file

Replace placeholders in file with parameter values from stack and optionally
from vault

positional arguments:
  file                  File to interpolate

optional arguments:
  -h, --help            show this help message and exit
  -s STACK, --stack STACK
                        Stack name for values. Automatically resolved on ec2
                        instances
  -v, --vault           Use vault values as well.Vault resovled from env
                        variables or default is used
  -o OUTPUT, --output OUTPUT
                        Output file
  -e ENCODING, --encoding ENCODING
                        Encoding to use for the file. Defaults to utf-8
```

### `ndt yaml-to-json`

```bash
usage: ndt yaml-to-json [-h] [--colorize] file

"Convert Nitor CloudFormation yaml to CloudFormation json with some
preprosessing

positional arguments:
  file            File to parse

optional arguments:
  -h, --help      show this help message and exit
  --colorize, -c  Colorize output
```

### `ndt ssh-hostkeys-collect`

```bash
/usr/bin/ssh-hostkeys-collect.sh: line 18: [: too many arguments
```

### `ndt print-create-instructions`

```bash
You can deploy the stack  by running 'ndt deploy-stack -h '
```

### `ndt source_infra_properties`

```bash
usage: /usr/local/bin/source_infra_properties.sh <component> [<stack-or-docker-name>]

Merges the properties of a component, stack and image from the relevant infra.properties and infra-<branch>.properties files.
This script is meant to be sourced to get the parameters into environment variables.
```

### `ndt create-shell-archive`

```bash
#!/bin/bash -e
umask 077
echo "Extracting -h"
```

### `ndt cf-stack-id`

```bash
usage: ndt cf-stack-id [-h]

Get id of the stack the creted this instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt undeploy-stack`

```bash
usage: /usr/local/bin/undeploy-stack.sh [-f] <component> <stack-name>

Undeploys (deletes) the given stack. Found s3 buckets are emptied and deleted only in case the -f argument is given.
```
