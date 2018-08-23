# Recommended parameters and workflow

There are a few parameters that affect how you set up your environments and how you
propagate changes through them. The parameters are the settings in `infra*.properties`
files that will be read before a template is pre-processed. The order of the files
processed is as follows:

* `infra.properties`
* `infra-[branch].properties`
* `[component]/infra.properties`
* `[component]/infra-[branch].properties`
* `[component]/(stack-|serverless-)[subcomponent]/infra.properties`
* `[component]/(stack-|serverless-)[subcomponent]/infra-[branch].properties`

Values later in the chain will override earlier values. As you can see, every
other value has the branch name in it. This means that you can change some
values for different branches so that you can account for the mandatory
differences between your environments.

## Important parameters

I will go through some parameters that effect how stacks work.

### `paramEnvId`

This parameter will be a part of default value for stack names, docker
repository urls and tags that mark baked images. The default value is the branch name if not set.

### `STACK_NAME`

You can set stack names to follow a scheme or set for each stack separately. For example
if you want to have the stack names start with the branch and then have the subcomponent
name you would set `STACK_NAME=${GIT_BRANCH}-$ORIG_STACK_NAME` in the root `infra.properties`
file. Defaults to `${COMPONENT}-${ORIG_STACK_NAME}-${paramEnvId}`

### `DOCKER_NAME`

Works the same way as `STACK_NAME` for docker repository urls. Defaults to
`[component]/$paramEnvId-$ORIG_DOCKER_NAME`

### `JENKINS_JOB_PREFIX`

The roots of ndt are in baking and deploying stacks via jenkins jobs, but this
parameter has effects besides jenkins jobs. It is part of the default tag that
baked AMI images are found with, which defaults to `${JENKINS_JOB_PREFIX}_[component]_bake`.
If you are using `generate-jobs.groovy` and [Jenkins DSL plugin](https://github.com/jenkinsci/job-dsl-plugin/wiki)
to create jobs for baking and deployments, this parameter is a part of the job
names as above, but also each unique job prefix is given a view with mathching
jobs in it. Defaults to `aws$paramEnvId`.