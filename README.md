# Nitor Deploy Tools

## Released version 1.0a28

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
usage: ndt detach-volume [-h] mount_path

Create a snapshot of a volume identified by it\'s mount path

positional arguments:
  mount_path  Where to mount the volume

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
usage: ndt ec2-instance-id [-h]

Get id for instance

optional arguments:
  -h, --help  show this help message and exit
```

### `ndt ec2-region`

```bash
usage: ndt ec2-region [-h]

Get default region - the region of the instance if run in an EC2 instance

optional arguments:
  -h, --help  show this help message and exit
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

Get the repo uri for a named docker

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
usage: ndt latest-snapshot [-h] tag

Get the latest snapshot with a given tag

positional arguments:
  tag         The tag to find snapshots with

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

### `ndt list-jobs`

```bash
usage: ndt list-jobs  [-h]

List jobs that should be created in jenkins for the current repository.
This includes all branches in the current repository.

optional arguments:
  -h, --help  show this help message and exit exit 1
fatal: Not a valid object name
```

### `ndt load-parameters`

```bash
usage: ndt load-parameters [-h] [--branch BRANCH]
                           [--stack STACK | --serverless SERVERLESS | --docker DOCKER | --image [IMAGE]]
                           [--json | --yaml | --properties | --export-statements]
                           [component]

Load parameters from infra*.properties files in the order: infra.properties,
infra-[branch].properties, [component]/infra.properties,
[component]/infra-[branch].properties, [component]/[subcomponent-
type]-[subcomponent]/infra.properties, [component]/[subcomponent-
type]-[subcomponent]/infra-[branch].properties Last parameter defined
overwrites ones defined before in the files. Supports parameter expansion and
bash -like transformations. Namely: ${PARAM##prefix} # strip prefix greedy
${PARAM%%suffix} # strip suffix greedy ${PARAM#prefix} # strip prefix not
greedy ${PARAM%suffix} # strip suffix not greedy ${PARAM:-default} # default
if empty ${PARAM:4:2} # start:len ${PARAM/substr/replace} ${PARAM^} # upper
initial ${PARAM,} # lower initial ${PARAM^^} # upper ${PARAM,,} # lower
Comment lines start with \'#\' Lines can be continued by adding \'\' at the end
See https://www.tldp.org/LDP/Bash-Beginners-Guide/html/sect_10_03.html (arrays
not supported)

positional arguments:
  component             Compenent to descend into

optional arguments:
  -h, --help            show this help message and exit
  --branch BRANCH, -b BRANCH
                        Branch to get active parameters for
  --stack STACK, -s STACK
                        CloudFormation subcomponent to descent into
  --serverless SERVERLESS, -l SERVERLESS
                        Serverless subcomponent to descent into
  --docker DOCKER, -d DOCKER
                        Docker image subcomponent to descent into
  --image [IMAGE], -i [IMAGE]
                        AMI image subcomponent to descent into
  --json, -j            JSON format output (default)
  --yaml, -y            YAML format output
  --properties, -p      properties file format output
  --export-statements, -e
                        Output as eval-able export statements
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
Prints out the instructions to create and deploy the resources in a stack
usage: ndt print-create-instructions [-h] component stack-name


positional arguments:
  component   the component directory where the stack template is
  stack-name  the name of the stack directory inside the component directory
              For example for ecs-cluster/stack-cluster/template.yaml
              you would give cluster

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
usage: ndt region [-h]

Get default region - the region of the instance if run in an EC2 instance

optional arguments:
  -h, --help  show this help message and exit
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
usage: ndt serverless-deploy [-h] component name

Deploys a Serverless Framework service under [component]/serverless-[name]

positional arguments:
  component   The component that contains the serverless service
  name        The name of the serverless service

optional arguments:
  -h, --help  show this help message and exit
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

Create a snapshot of a volume identified by it\'s mount path

positional arguments:
  tag_key     Key of the tag to find volume with
  tag_value   Value of the tag to find volume with
  mount_path  Where to mount the volume

optional arguments:
  -h, --help  show this help message and exit
  -w, --wait  Wait for the snapshot to finish before returning
```

### `ndt undeploy-stack`

```bash
usage: ndt undeploy-stack [-h] [-f] <component> <stack-name>

Undeploys (deletes) the given stack.
Found s3 buckets are emptied and deleted only in case the -f argument is given.

positional arguments:
  component   the component directory where the stack template is
  stack-name  the name of the stack directory inside the component directory
              For example for ecs-cluster/stack-cluster/template.yaml
              you would give cluster

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

### `ndt volume-from-snapshot`

```bash
usage: ndt volume-from-snapshot [-h] [-n]
                                tag_key tag_value mount_path [size_gb]
ndt volume-from-snapshot: error: Only makes sense on an EC2 instance
```

### `ndt yaml-to-json`

```bash
usage: ndt yaml-to-json [-h] [--colorize] file

Convert Nitor CloudFormation yaml to CloudFormation json with some
preprosessing

positional arguments:
  file            File to parse

optional arguments:
  -h, --help      show this help message and exit
  --colorize, -c  Colorize output
```

### `ndt yaml-to-yaml`

```bash
usage: ndt yaml-to-yaml [-h] [--colorize] file

Do ndt preprocessing for a yaml file

positional arguments:
  file            File to parse

optional arguments:
  -h, --help      show this help message and exit
  --colorize, -c  Colorize output
```

### `[ndt ]associate-eip`

```bash
usage: associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
                     [-p ALLOCATIONIDPARAM]

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        Elastic IP to allocate - default is to get paramEip
                        from the stack that created this instance
  -a ALLOCATIONID, --allocationid ALLOCATIONID
                        Elastic IP allocation id to allocate - default is to
                        get paramEipAllocationId from the stack that created
                        this instance
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

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]ec2-associate-eip`

```bash
usage: ec2-associate-eip [-h] [-i IP] [-a ALLOCATIONID] [-e EIPPARAM]
                         [-p ALLOCATIONIDPARAM]

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        Elastic IP to allocate - default is to get paramEip
                        from the stack that created this instance
  -a ALLOCATIONID, --allocationid ALLOCATIONID
                        Elastic IP allocation id to allocate - default is to
                        get paramEipAllocationId from the stack that created
                        this instance
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

positional arguments:
  file        File to follow

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]n-include`

```bash
usage: n-include [-h] file

positional arguments:
  file        The file to find

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]n-include-all`

```bash
usage: n-include-all [-h] pattern

positional arguments:
  pattern     The file pattern to find

optional arguments:
  -h, --help  show this help message and exit
```

### `[ndt ]signal-cf-status`

```bash
usage: signal-cf-status [-h] [-r RESOURCE] status

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
/home/pasi/.pyenv/versions/3.6.5/bin/ensure-letsencrypt-certs.sh: line 23: fetch-secrets.sh: command not found
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

