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

## Commands


