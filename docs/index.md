# Nitor Deploy Tools
[![Build Status](https://travis-ci.org/NitorCreations/nitor-deploy-tools.svg?branch=master)](https://travis-ci.org/NitorCreations/nitor-deploy-tools)
[![Coverage Status](https://coveralls.io/repos/github/NitorCreations/nitor-deploy-tools/badge.svg?branch=master)](https://coveralls.io/github/NitorCreations/nitor-deploy-tools?branch=master)

## Released version 0.223

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

nitor-deploy-tools works by defining _Amazon Machine Images_, _Docker containers_,
_Serverless services_ and deploying _[CloudFormation](https://aws.amazon.com/cloudformation/)
stacks_ of resources.

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

Optionally you can add the argument `--project-env` to add a `PROMPT_COMMAND` hook for bash to check git
local variables to export a useful project environmnet that usually points to AWS credentials profile.
This could also be a script that assumes a role for you even including MFA authentication. The script
is run for every prompt though inside the project so you will want to make it check if the session is still
valid before trying to assume the role. You can use then environment variable `AWS_SESSION_EXPIRATION` that
is set by `ndt assume-role` to only assume role when the previous role has expired. See section about
TOTP MFA codes below. An example of what a sourceable role script could be is below:

```bash
#!/bin/bash

# Reset variables potentially set by other projects
unset AWS_PROFILE AWS_DEFAULT_PROFILE
export AWS_DEFAULT_REGION=eu-central-1

ADMIN_ROLE="arn:aws:iam::432486532345:role/my-admin-role"
# Check that the current role matches the one we want
if [ "$AWS_ROLE_ARN" != "$ADMIN_ROLE" ]; then
  unset AWS_SESSION_EXPIRATION
fi
EXP_DATE=$(date +%s -d "$AWS_SESSION_EXPIRATION")
NOW=$(date +%s)
#Check that the session is still valid
if [ $NOW -lt $EXP_DATE  ]; then
  exit 0
fi
# Set the credentials that have access to the role
export AWS_PROFILE=myprofile AWS_DEFAULT_PROFILE=myprofile
# Reset wrong or expired variables
unset AWS_SESSION_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_EXPIRATION AWS_ROLE_ARN
eval $(ndt assume-role -t mytoken "$ADMIN_ROLE")
# Reset profile to make the assumed role take over
unset AWS_PROFILE AWS_DEFAULT_PROFILE
```

Note that the date command is different on OSX: https://unix.stackexchange.com/questions/84381/how-to-compare-two-dates-in-a-shell

So taking project environment variables into use with your command completion would require setting

```bash
eval "$(nitor-dt-register-complete --project-env)"
```

Somewehere in your bash profile files - I have mine in `~/.bashrc`

The checked git local configurations are:
* `ndt.source.env` - source a file on every prompt
* `ndt.aws.profile` - export the name of an aws credentials profile on every prompt
* `ndt.aws.region` - export a default region name on every prompt

You can set these variables by calling `git config [variable] [value]` and you can check the commands
that would be executed by calling `nitor-dt-load-project-env`

So to complete the script example from above, you would put the script somewhere handy to execute -
say `~/bin/my-admin-role` if you have that on your `PATH`. Then you would just set that to be
sourced in your ndt project by calling `git config ndt.source.env my-admin-role` in your project
that needs that role and assuming you've set up command completion as above, every time you
change directory into the project, your credentials get set up automatically for you to work and
checked every time you give a command.

## Template pre-processing

For `ndt deploy-stack`, `ndt deploy-serverless`, `ndt yaml-to-json` and `ndt yaml-to-yaml` there
is a template pre-processing step that is fairly important. The pre-processing implements some
client side functionality that greatly improves the usability and modularisation of stacks and
serverless projects. The flow of the prosessing is roughly as follows:

* Resolve ndt parameters from `infra*.properties` files along the path to the template
* Expand and resolve the parameter section for the template to get all the parameters
  actually in use in the template
* Expand the rest of the template verifying all parameter references
* `TODO` All values that use `${parameter}` notation will be filled in as the template is pre-procesed.
* `Ref: parameter` references will be posted to CloudFormation as-is

### Pre-processing functions

There are a few usefull fuction you can insert and use in the pre-processing phase

#### `Fn::ImportYaml`

Imports an external yaml file into the place occupied with this function. Example:

```yaml
Parameters:
  { 'Fn::ImportYaml': ../../common-params.yaml,
      ssh-key: my-key,
      dns: myinstence.example.com,
      zone: example.com.,
      instance: m4.large }

```

The fields in the same object as the function will be used to fill in references with the
notation `((parameter))` in the target yaml. Example of the target:

```yaml
paramSshKeyName:
  Description: SSH key for AMIBakery
  Type: String
  Default: ((ssh-key))
paramDnsName:
  Description: DNS name for AMIBakery
  Type: String
  Default: ((dns))
paramHostedZoneName:
  Description: Route 53 hosted zone name
  Type: String
  Default: ((zone))
paramInstanceType:
  Description: Instance type for AMIBakery
  Type: String
  Default: ((instance))
```

The filename of the import may contain parameters in the form `${parameter}` and that will be resolved
before include.

#### `Fn::Merge`

Often you will want to merge an imported yaml snippet into an existing list and this function does that.
Example:

```yaml
Parameters:
  'Fn::Merge':
  - { 'Fn::ImportYaml': ../../common-params.yaml,
      ssh-key: my-key,
      dns: myinstance.example.com,
      zone: nitor.zone.,
      instance: m3.large,
      eip: 51.51.111.91 }
  - paramJenkinsGit:
      Description: git repo for AMIBakery
      Type: String
      Default: ''
```
#### `Fn::ImportFile`

Imports a file in place of the function. Useful for files you want to manage externally to the
template as for example userdata shell scripts or AppSync schemas or the like. Importing
does a few useful tricks:

* Resolves parameter references with a few different notations to fit into different scripting files
* Encodes the result into a list of json strings, one string per line and adds in the appropriate escapes

##### Parameter notations

Shell scripts usually most simply can define environment variables with the prefix `CF_` and the
rest of the name will be the name of the parameter that will be inserted as a reference to the value.

Example:
```bash
CF_AWS__StackName=
CF_AWS__Region=
CF_paramAmiName=
CF_paramAdditionalFiles=
CF_paramAmi=
CF_paramDeployToolsVersion=
CF_paramDnsName=
CF_paramEip=
CF_extraScanHosts=`#optional`
CF_paramMvnDeployId=`#optional`
```

This is transformed into
```json
[
  "#!/bin/bash -x\n",
  "\n",
  "CF_AWS__StackName='",
  {
    "Ref": "AWS::StackName"
  },
  "'\n",
  "CF_AWS__Region='",
  {
    "Ref": "AWS::Region"
  },
  "'\n",
  "CF_paramAmiName='",
  {
    "Ref": "paramAmiName"
  },
  "'\n",
  "CF_paramAdditionalFiles='",
  {
    "Ref": "paramAdditionalFiles"
  },
  "'\n",
  "CF_paramAmi='",
  {
    "Ref": "paramAmi"
  },
  "'\n",
  "CF_paramDeployToolsVersion='",
  {
    "Ref": "paramDeployToolsVersion"
  },
  "'\n",
  "CF_paramDnsName='",
  {
    "Ref": "paramDnsName"
  },
  "'\n",
  "CF_paramEip='",
  {
    "Ref": "paramEip"
  },
  "'\n",
  "CF_extraScanHosts='",
  "",
  "'\n",
  "CF_paramMvnDeployId='",
  "",
  "'\n"
]
```

Note how CloudFormation internal parameters are avaible via `CF_AWS__StackName` to `"Ref": "AWS::StackName"`
type transformation. Suffixing a paremter with `#optional` will result in no error being thrown if the
parameter is not present in the stack and in that case the value will simply be empty instead of a
reference.

Raw cloudformation json can be inserted with the notation `#CF{ myContent }`. Example:

```bash
NEW_RELIC_LICENSE_KEY=#CF{ "Ref": "paramNewRelicLicenseKey" }
```

Also works with javascript type comments:
```javascript
const stackName = //CF{ "Ref": "AWS::StackName" }
```

### `StackRef`

Gets either a input or output parameter or logical resource of another stack as the value to substitute the
function. Neither parameter nor resources need to be exported to be available, which makes this somewhat
more flexible that CloudFormation native Export/Import. The substitution is completely client-side so
referencing stacks will not be modified in any way if referenced staks change. Later there will be tooling to
manage changes across several stacks in the same repository that refer to eachother. You can run
`ndt show-stack-params-and-outputs [stack-name]` to see the parameters and resources that are available
in each stack.

## Working with TOTP MFA tokens

Ndt includes tools to import, use and backup TOTP MFA tokens. Notably the `ndt assume-role` command
can use as an argument a name of an MFA token to make it easy to assume roles that require TOTP
MFA authentication.

### Importing

It is recommended that you import MFA codes from whatever place offers them to NDT first and then
use that to import the code to whatever other device that needs it. Importing is done with `ndt mfa-add-code`.
For the AWS console you would start by adding the MFA device to the IAM user
(IAM -> Users -> [Find user] -> Security credentials -> Assigned MFA device -> Edit) and choosing
"A virtual MFA device". Clicking "Next Step" twice will give you the qr code of the shared secret
and clicking "Show secret key for manual configuration" will give you the shared secret as text,
which is what ndt needs.

You can now go to the terminal and type in `ndt mfa-add-code -i mytokenname`. The name you give
here is the one you will be using on the command line to generate codes when needed so make
it easy to type and memorable. Ndt will ask for the secret that you can then cut and paste from
the console to the terminal. Next ndt will give you two consecutive codes that you can then
paste back into the console. Once this is done, ndt will still ask you for the ARN of the MFA
device, which is needed to interact with the api calls that use the token. If you are adding
a non-AWS token you can ignore this.

Ndt saves the token in `~/.ndt/mfa_mytokenname` and the secret is encrypted with a key that is
derived from your computers uuid. This means that those files are only usable on the machine
that you added the codes on.

### Using

The simplest use of the code is getting a TOTP code from the command line by calling `ndt mfa-code mytokenname`
The code printed can then be copied into whatever place is requesting it. Another very
handy use is to pass it to `ndt assume-role` to make assuming roles that require MFA easy.

A common practice is to create a sourceable file somewhere on your PATH (maybe `~/bin/`?)
that makes assuming roles just a matter of sourcing that file. Say you were to create the file
`~/bin/extadmin` (and `~/bin/` is on your PATH):

```bash
#!/bin/bash
export AWS_DEFAULT_REGION=eu-west-1 AWS_PROFILE=myprofile
unset AWS_SESSION_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
eval $(ndt assume-role -t mytokenname arn:aws:iam::223587298868:role/EXTAdmin)
unset AWS_PROFILE AWS_DEFAULT_PROFILE
```

Then assuming that role would simply be typing `. extadmin` in the terminal. That would also
be protected by the mfa codes that are only usable on your computer.

### Backing up

There are two ways to back up your tokens. The tokens will not be usable directly on any
other computer and that includes a re-installed OS on the same computer.
`ndt mfa-backup`, given an encryption password, will print out your tokens as an encrypted
string that contains decrypted secrets of all your tokens. You can put that then in a file
and store that in a safe place in case you need to recreate the tokens at some point.

The other way is to generate a QR code for each token and import them that way into another
device. The code is simply printed to the terminal with `ndt mfa-qrcode mytokenname`

## Commands


