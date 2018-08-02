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
