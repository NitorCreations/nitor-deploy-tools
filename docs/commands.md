# NDT Command Reference

## `ndt account-id`

```bash
usage: ndt account-id [-h]

Get current account id. Either from instance metadata or current cli
configuration.

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt add-deployer-server`

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

## `ndt assume-role`

```bash
usage: ndt assume-role [-h] [-t TOKEN_NAME] [-d DURATION] [-p PROFILE]
                       role_arn

Assume a defined role. Prints out environment variables to be eval\'d to
current context for use: eval $(ndt assume-role
\'arn:aws:iam::43243246645:role/DeployRole\')

positional arguments:
  role_arn              The ARN of the role to assume

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN_NAME, --mfa-token TOKEN_NAME
                        Name of MFA token to use
  -d DURATION, --duration DURATION
                        Duration for the session in minutes
  -p PROFILE, --profile PROFILE
                        Profile to edit in ~/.aws/credentials to make role
                        persist in that file for the duration of the session.
```

## `ndt assumed-role-name`

```bash
usage: ndt assumed-role-name [-h]

Read the name of the assumed role if currently defined

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt bake-docker`

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

## `ndt bake-image`

```bash
usage: ndt bake-image [-h] component [image-name]

Runs an ansible playbook that  builds an Amazon Machine Image (AMI) and
tags the image with the job name and build number.

positional arguments
  component     the component directory where the ami bake configurations are
  [image-name]  Optional name for a named image in component/image-[image-name]

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-delete-stack`

```bash
usage: ndt cf-delete-stack [-h] stack_name region

Delete an existing CloudFormation stack

positional arguments:
  stack_name  Name of the stack to delete
  region      The region to delete the stack from

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-follow-logs`

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

## `ndt cf-get-parameter`

```bash
usage: ndt cf-get-parameter [-h] parameter

Get a parameter value from the stack

positional arguments:
  parameter   The name of the parameter to print

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-logical-id`

```bash
usage: ndt cf-logical-id [-h]

Get the logical id that is expecting a signal from this instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-region`

```bash
usage: ndt cf-region [-h]

Get region of the stack that created this instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-signal-status`

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

## `ndt cf-stack-id`

```bash
usage: ndt cf-stack-id [-h]

Get id of the stack the creted this instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt cf-stack-name`

```bash
usage: ndt cf-stack-name [-h]

Get name of the stack that created this instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt create-account`

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

## `ndt create-stack`

```bash
usage: ndt create-stack [-h] [-y] [template]

Create a stack from a template

positional arguments:
  template

optional arguments:
  -h, --help  show this help message and exit
  -y, --yes   Answer yes or use default to all questions
```

## `ndt deploy-cdk`

```bash
usage: ndt deploy-cdk [-d] [-h] component cdk-name

Exports ndt parameters into component/cdk-name/variables.json, runs pre_deploy.sh in the
cdk project and runs cdk diff; cdk deploy for the same

positional arguments:
  component   the component directory where the cdk directory is
  cdk-name the name of the cdk directory that has the template
                  For example for lambda/cdk-sender/bin/MyProject.ts
                  you would give sender

optional arguments:
  -d, --dryrun  dry-run - do only parameter expansion and pre_deploy.sh and cdk diff
  -h, --help    show this help message and exit
```

## `ndt deploy-serverless`

```bash
usage: ndt deploy-serverless [-d] [-h] component serverless-name

Exports ndt parameters into component/serverless-name/variables.yml, runs npm i in the
serverless project and runs sls deploy -s $paramEnvId for the same

positional arguments:
  component   the component directory where the serverless directory is
  serverless-name the name of the serverless directory that has the template
                  For example for lambda/serverless-sender/template.yaml
                  you would give sender

optional arguments:
  -d, --dryrun  dry-run - do only parameter expansion and template pre-processing and npm i
  -h, --help    show this help message and exit
```

## `ndt deploy-stack`

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
  -d, --dryrun  dry-run - show only the change set without actually deploying it
  -h, --help  show this help message and exit
```

## `ndt deploy-terraform`

```bash
usage: ndt deploy-terraform [-d] [-h] component terraform-name

Exports ndt parameters into component/terraform-name/terraform.tfvars as json, runs pre_deploy.sh in the
terraform project and runs terraform plan; terraform apply for the same

positional arguments:
  component   the component directory where the terraform directory is
  terraform-name the name of the terraform directory that has the template
                  For example for lambda/terraform-sender/template.yaml
                  you would give sender

optional arguments:
  -d, --dryrun  dry-run - do only parameter expansion and template pre-processing and npm i
  -h, --help    show this help message and exit
```

## `ndt detach-volume`

```bash
usage: ndt detach-volume [-h] mount_path

Create a snapshot of a volume identified by it\'s mount path

positional arguments:
  mount_path  Where to mount the volume

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ec2-clean-snapshots`

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

## `ndt ec2-get-tag`

```bash
usage: ndt ec2-get-tag [-h] name

Get the value of a tag for an ec2 instance

positional arguments:
  name        The name of the tag to get

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ec2-get-userdata`

```bash
usage: ndt ec2-get-userdata [-h] file

Get userdata defined for an instance into a file

positional arguments:
  file        File to write userdata into

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ec2-instance-id`

```bash
usage: ndt ec2-instance-id [-h]

Get id for instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ec2-region`

```bash
usage: ndt ec2-region [-h]

Get default region - the region of the instance if run in an EC2 instance

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ec2-wait-for-metadata`

```bash
usage: ndt ec2-wait-for-metadata [-h] [--timeout TIMEOUT]

Waits for metadata service to be available. All errors are ignored until time
expires or a socket can be established to the metadata service

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT, -t TIMEOUT
                        Maximum time to wait in seconds for the metadata
                        service to be available
```

## `ndt ecr-ensure-repo`

```bash
usage: ndt ecr-ensure-repo [-h] name

Ensure that an ECR repository exists and get the uri and login token for it

positional arguments:
  name        The name of the ecr repository to verify

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt ecr-repo-uri`

```bash
usage: ndt ecr-repo-uri [-h] name

Get the repo uri for a named docker

positional arguments:
  name        The name of the ecr repository

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt enable-profile`

```bash
usage: ndt enable-profile [-h] [-i | -a | -n] profile

Enable a configured profile. Simple IAM user, AzureAD and ndt assume-role
profiles are supported

positional arguments:
  profile      The profile to enable

optional arguments:
  -h, --help   show this help message and exit
  -i, --iam    IAM user type profile
  -a, --azure  Azure login type profile
  -n, --ndt    NDT assume role type profile
```

## `ndt get-images`

```bash
usage: ndt get-images [-h] job_name

Gets a list of images given a bake job name

positional arguments:
  job_name    The job name to look for

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt interpolate-file`

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

## `ndt json-to-yaml`

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

## `ndt latest-snapshot`

```bash
usage: ndt latest-snapshot [-h] tag

Get the latest snapshot with a given tag

positional arguments:
  tag         The tag to find snapshots with

optional arguments:
  -h, --help  show this help message and exit
```

## `ndt list-components`

```bash
usage: ndt list-components [-h] [-j] [-b BRANCH]

Prints the components in a branch, by default the current branch

optional arguments:
  -h, --help            show this help message and exit
  -j, --json            Print in json format.
  -b BRANCH, --branch BRANCH
                        The branch to get components from. Default is to
                        process current branch
```

## `ndt list-file-to-json`

```bash
