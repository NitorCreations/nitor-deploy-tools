# Nitor Deploy Tools

## Released version 

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
  File "/usr/local/bin/ndt", line 9, in <module>
    load_entry_point(\'nitor-deploy-tools==0.214\', \'console_scripts\', \'ndt\')()
  File "/usr/local/lib/python2.7/dist-packages/n_utils/cli.py", line 165, in ndt
    my_func()
  File "/usr/local/lib/python2.7/dist-packages/n_utils/cli.py", line 227, in get_account_id
    print cf_utils.resolve_account()
  File "/usr/local/lib/python2.7/dist-packages/n_utils/cf_utils.py", line 389, in resolve_account
    return sts.get_caller_identity()[\'Account\']
  File "/usr/local/lib/python2.7/dist-packages/botocore/client.py", line 324, in _api_call
    return self._make_api_call(operation_name, kwargs)
  File "/usr/local/lib/python2.7/dist-packages/botocore/client.py", line 622, in _make_api_call
    raise error_class(parsed_response, operation_name)
botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId) when calling the GetCallerIdentity operation: The security token included in the request is invalid.
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
+ image=-h
+ shift
+ \'[\' -h \']\'
+ docker=
+ shift
```

### `ndt bake-image`

```bash
+ image=-h
+ shift
+ \'[\' -h \']\'
+ source source_infra_properties.sh -h \'\'
++ \'[\' \'\' \']\'
++ \'[\' \'\' \']\'
+++ git rev-parse --abbrev-ref HEAD
++ GIT_BRANCH=master
++ GIT_BRANCH=master
++ image=-h
++ shift
++ ORIG_STACK_NAME=
++ ORIG_DOCKER_NAME=
++ shift
++ STACK_NAME=master-
++ DOCKER_NAME=-h/master-
++ sharedpropfile=infra.properties
++ imagesharedpropfile=-h/infra.properties
++ stacksharedpropfile=-h/stack-/infra.properties
++ dockersharedpropfile=-h/docker-/infra.properties
++ infrapropfile=infra-master.properties
++ imagepropfile=-h/infra-master.properties
++ stackpropfile=-h/stack-/infra-master.properties
++ dockerpropfile=-h/docker-/infra-master.properties
++ source_first_existing infra.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e infra.properties \']\'
++ source_first_existing infra-master.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e infra-master.properties \']\'
++ source_first_existing -h/infra.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/infra.properties \']\'
++ source_first_existing -h/infra-master.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/infra-master.properties \']\'
++ source_first_existing -h/stack-/infra.properties -h/docker-/infra.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/stack-/infra.properties \']\'
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/docker-/infra.properties \']\'
++ source_first_existing -h/stack-/infra-master.properties -h/docker-/infra-master.properties
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/stack-/infra-master.properties \']\'
++ for PROPFILE in \'"$@"\'
++ \'[\' -e -h/docker-/infra-master.properties \']\'
++ \'[\' \'\' \']\'
+++ ec2-region
++ REGION=eu-central-1
++ \'[\' \'\' \']\'
+++ account-id
Traceback (most recent call last):
  File "/usr/local/bin/account-id", line 9, in <module>
    load_entry_point(\'nitor-deploy-tools==0.214\', \'console_scripts\', \'account-id\')()
  File "/usr/local/lib/python2.7/dist-packages/n_utils/cli.py", line 227, in get_account_id
    print cf_utils.resolve_account()
  File "/usr/local/lib/python2.7/dist-packages/n_utils/cf_utils.py", line 389, in resolve_account
    return sts.get_caller_identity()[\'Account\']
  File "/usr/local/lib/python2.7/dist-packages/botocore/client.py", line 324, in _api_call
    return self._make_api_call(operation_name, kwargs)
  File "/usr/local/lib/python2.7/dist-packages/botocore/client.py", line 622, in _make_api_call
    raise error_class(parsed_response, operation_name)
botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId) when calling the GetCallerIdentity operation: The security token included in the request is invalid.
++ ACCOUNT_ID=
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
ndt cf-logical-id: error: Only makes sense on an EC2 instance cretated from a CF stack
```

### `ndt cf-region`

```bash
usage: ndt cf-region [-h]
ndt cf-region: error: Only makes sense on an EC2 instance cretated from a CF stack
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
ndt cf-stack-id: error: Only makes sense on an EC2 instance cretated from a CF stack
```

### `ndt cf-stack-name`

```bash
usage: ndt cf-stack-name [-h]
ndt cf-stack-name: error: Only makes sense on an EC2 instance cretated from a CF stack
```

### `ndt create-account`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
```

### `ndt create-stack`

```bash
usage: ndt create-stack [-y] [-h] template
ndt create-stack: error: too few arguments
```

### `ndt deploy-serverless`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
```

### `ndt deploy-stack`

```bash
+ \'[\' -h = -d \']\'
+ image=-h
+ shift
+ stackName=
+ shift
```

### `ndt detach-volume`

```bash
usage: ndt detach-volume [-h] mount_path
ndt detach-volume: error: Only makes sense on an EC2 instance
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

### `ndt ec2-get-tag`

```bash
usage: ndt ec2-get-tag [-h] name

Get the value of a tag for an ec2 instance

positional arguments:
  name        The name of the tag to get

optional arguments:
  -h, --help  show this help message and exit
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

### `ndt ec2-instance-id`

```bash

```

### `ndt ec2-region`

```bash
eu-central-1
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

### `ndt ecr-repo-uri`

```bash
usage: ndt ecr-repo-uri [-h] name

Ensure that an ECR repository exists and get the uri and login token for it

positional arguments:
  name        The name of the ecr repository

optional arguments:
  -h, --help  show this help message and exit
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

### `ndt latest-snapshot`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
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

### `ndt list-jobs`

```bash

```

### `ndt load-parameters`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
```

### `ndt mfa-add-token`

```bash
usage: ndt mfa-add-token [-h] [-i] [-a TOKEN_ARN] [-s TOKEN_SECRET] [-f]
                         token_name

Adds an MFA token to be used with role assumption. Tokens will be saved in a
.ndt subdirectory in the user\'s home directory. If a token with the same name
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

### `ndt mfa-code`

```bash
usage: ndt mfa-code [-h] token_name

Generates a TOTP code using an MFA token.

positional arguments:
  token_name  Name of the token to use.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt mfa-delete-token`

```bash
usage: ndt mfa-delete-token [-h] token_name

Deletes an MFA token file from the .ndt subdirectory in the user\'s home
directory

positional arguments:
  token_name  Name of the token to delete.

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt print-create-instructions`

```bash
You can deploy the stack  by running \'ndt deploy-stack -h \'
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

### `ndt pytail`

```bash
usage: ndt pytail [-h] file

Read and print a file and keep following the end for new data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt region`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
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

### `ndt serverless-deploy`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
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

### `ndt snapshot-from-volume`

```bash
usage: ndt snapshot-from-volume [-h] [-w] tag_key tag_value mount_path
ndt snapshot-from-volume: error: Only makes sense on an EC2 instance
```

### `ndt undeploy-stack`

```bash
+ \'[\' -h == -f \']\'
+ image=-h
+ shift
+ stackName=
+ shift
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

### `ndt volume-from-snapshot`

```bash
usage: ndt volume-from-snapshot [-h] [-n]
                                tag_key tag_value mount_path [size_gb]
ndt volume-from-snapshot: error: Only makes sense on an EC2 instance
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

### `ndt yaml-to-yaml`

```bash
usage: ndt <command> [args...]
	command shoud be one of:
		account-id
		add-deployer-server
		associate-eip
		assume-role
		bake-docker
		bake-image
		cf-delete-stack
		cf-follow-logs
		cf-get-parameter
		cf-logical-id
		cf-logs-to-cloudwatch
		cf-region
		cf-signal-status
		cf-stack-id
		cf-stack-name
		create-shell-archive
		create-stack
		deploy-stack
		detach-volume
		ec2-associate-eip
		ec2-clean-snapshots
		ec2-get-tag
		ec2-get-userdata
		ec2-instance-id
		ec2-region
		ecr-ensure-repo
		ecr-repo-uri
		encrypt-and-mount
		ensure-letsencrypt-certs
		get-images
		hook
		interpolate-file
		json-to-yaml
		lastpass-fetch-notes
		lastpass-login
		lastpass-logout
		letsencrypt
		list-file-to-json
		list-jobs
		logs-to-cloudwatch
		lpssh
		mfa-add-token
		mfa-code
		mfa-delete-token
		n-include
		n-include-all
		n-utils-init
		print-create-instructions
		promote-image
		pytail
		register-private-dns
		s3-role-download
		setup-cli
		setup-fetch-secrets
		share-to-another-region
		show-stack-params-and-outputs
		signal-cf-status
		snapshot-from-volume
		source_infra_properties
		ssh-hostkeys-collect
		undeploy-stack
		upsert-cloudfront-records
		volume-from-snapshot
		yaml-to-json
```

### `[ndt ]associate-eip`

```bash
usage: associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
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

### `[ndt ]cf-logs-to-cloudwatch`

```bash
usage: cf-logs-to-cloudwatch [-h] file

Read a file and send rows to cloudwatch and keep following the end for new
data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]ec2-associate-eip`

```bash
usage: ec2-associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
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

### `[ndt ]logs-to-cloudwatch`

```bash
usage: logs-to-cloudwatch [-h] file

Read a file and send rows to cloudwatch and keep following the end for new
data

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]n-include`

```bash
usage: n-include [-h] file

Find a file from the first of the defined include paths

positional arguments:
  file        The file to find

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]n-include-all`

```bash
usage: n-include-all [-h] pattern

Find a file from the first of the defined include paths

positional arguments:
  pattern     The file pattern to find

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]signal-cf-status`

```bash
usage: signal-cf-status [-h] [-r RESOURCE] status

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

### `create-shell-archive.sh`

```bash
usage: /usr/local/bin/create-shell-archive.sh [<file> ...]
Creates a self-extracting bash archive, suitable for storing in e.g. Lastpass SecureNotes
```

### `encrypt-and-mount.sh`

```bash
\'-h\' not a block device
Usage: /usr/local/bin/encrypt-and-mount.sh blk-device mount-path
```

### `ensure-letsencrypt-certs.sh`

```bash
