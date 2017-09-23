#!/bin/bash

# Copyright 2016-2017 Nitor Creations Oy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


if [ "$_ARGCOMPLETE" ]; then
  unset _ARGCOMPLETE
  source $(n-include autocomplete-helpers.sh)
  # Handle command completion executions
  case $COMP_CWORD in
    2)
      compgen -W "$(get_bakeable_images)" -- $COMP_CUR
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi

set -xe

die () {
  echo "$@" >&2
  exit 1
}

image="$1" ; shift
[ "${image}" ] || die "You must give the image name as argument"

source source_infra_properties.sh "$image" ""

[ ! -d .cache ] || rm -rf .cache
mkdir .cache

cache () {
  if ! [ -d .cache ]; then
      mkdir -p .cache
  fi
  args=${*}
  cachefile=.cache/"${args//[\"\'\ -\*]/_}"
  if [ -e "$cachefile" ]; then
    cat $cachefile
  else
    "$@" | tee $cachefile
  fi
}

# Set defaults if not customized

if ! [ "$SSH_USER" ]; then
  if [ "$IMAGETYPE" = "windows" ]; then
    SSH_USER="Administrator"
  else
    SSH_USER="$IMAGETYPE"
  fi
fi
[ "$NETWORK_STACK" ] || NETWORK_STACK=infra-network
[ "$PRIVATE_SUBNET" ] || PRIVATE_SUBNET="no"
if ! [ "$NETWORK_PARAMETER" ]; then
  if [ "$PRIVATE_SUBNET" = "yes" ]; then
    NETWORK_PARAMETER=subnetPrivInfraB
  else
    NETWORK_PARAMETER=subnetInfraB
  fi
fi
[ "$SUBNET" ] || SUBNET="$(cache ndt show-stack-params-and-outputs -r $REGION $NETWORK_STACK | jq -r .$NETWORK_PARAMETER)"
if ! [ "$SECURITY_GROUP" ]; then
  if [ "$IMAGETYPE" != "windows" ]; then
    SG_PARAM=".bakeInstanceSg"
  else
    SG_PARAM=".bakeWinInstanceSg"
  fi
  SECURITY_GROUP="$(cache ndt show-stack-params-and-outputs -r $REGION bakery-roles | jq -r $SG_PARAM)"
fi
[ "$AMIBAKE_INSTANCEPROFILE" ] || AMIBAKE_INSTANCEPROFILE="$(cache ndt show-stack-params-and-outputs -r $REGION bakery-roles | jq -r .bakeInstanceInstanceprofile)"
[ "$PAUSE_SECONDS" ] || PAUSE_SECONDS=15
for var in REGION SUBNET SECURITY_GROUP AMIBAKE_INSTANCEPROFILE ; do
  [ "${!var}" ] || die "Could not determine $var automatically. Please set ${var} manually in ${infrapropfile}"
done

for var in AWS_KEY_NAME paramDeployToolsVersion; do
  [ "${!var}" ] || die "Please set ${var} in ${sharedpropfile}"
done

for var in IMAGETYPE APP_USER APP_HOME SSH_USER; do
  [ "${!var}" ] || die "Please set ${var} in ${infrapropfile}"
done

imagedir=${image}/image

VAR_AMI="AMIID_${IMAGETYPE}"
AMI="${!VAR_AMI}"

[ "$AMI" ] || die "Please set AMIID_$IMAGETYPE in ${infrapropfile}"

TSTAMP=$(date +%Y%m%d%H%M%S)

cleanup() {
  if [ "$IMAGETYPE" != "windows" ]; then
    eval $(ssh-agent -k)
  fi
}
trap cleanup EXIT
if [ "$IMAGETYPE" != "windows" ]; then
  eval $(ssh-agent)
  if ! [ -e $HOME/.ssh/$AWS_KEY_NAME -o -e $HOME/.ssh/$AWS_KEY_NAME.pem \
         -o -e $HOME/.ssh/$AWS_KEY_NAME.rsa ]; then
    fetch-secrets.sh get 600 --optional "$HOME/.ssh/$AWS_KEY_NAME" \
        "$HOME/.ssh/$AWS_KEY_NAME.pem" "$HOME/.ssh/$AWS_KEY_NAME.rsa" ||:
  fi
  if [ -r "$HOME/.ssh/$AWS_KEY_NAME" ]; then
    ssh-add "$HOME/.ssh/$AWS_KEY_NAME"
  elif [ -r "$HOME/.ssh/$AWS_KEY_NAME.pem" ]; then
    ssh-add "$HOME/.ssh/$AWS_KEY_NAME.pem"
  elif [ -r "$HOME/.ssh/$AWS_KEY_NAME.rsa" ]; then
    ssh-add "$HOME/.ssh/$AWS_KEY_NAME.rsa"
  else
    die "Failed to find ssh private key"
  fi
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]="prepare_script=$(n-include prepare.sh)"
else
  WIN_PASSWD="$(tr -cd '[:alnum:]' < /dev/urandom | head -c16)"
  PASSWD_ARG="{\"ansible_ssh_pass\": \"$WIN_PASSWD\","
  PASSWD_ARG="$PASSWD_ARG \"ansible_winrm_operation_timeout_sec\": 60,"
  PASSWD_ARG="$PASSWD_ARG \"ansible_winrm_read_timeout_sec\": 70,"
  PASSWD_ARG="$PASSWD_ARG \"ansible_winrm_server_cert_validation\": \"ignore\","
  PASSWD_ARG="$PASSWD_ARG \"prepare_script\": \"$(n-include prepare.ps1)\"}"
fi
if [ -z "$BUILD_NUMBER" ]; then
  BUILD_NUMBER=$TSTAMP
else
  BUILD_NUMBER=$(printf "%04d\n" $BUILD_NUMBER)
fi
if [ -z "$JOB_NAME" ]; then
  JOB_NAME="${JENKINS_JOB_PREFIX}-${image}-bake"
fi
if [ "$IMAGETYPE" != "windows" ]; then
  if ! [ -r $imagedir/pre_install.sh ]; then
    echo -e "#!/bin/bash\n\nexit 0" > $imagedir/pre_install.sh
  fi
  if ! [ -r $imagedir/post_install.sh ]; then
    echo -e "#!/bin/bash\n\nexit 0" > $imagedir/post_install.sh
  fi
else
  if ! [ -r $imagedir/pre_install.ps1 ]; then
    echo -e "exit 0\r" > $imagedir/pre_install.ps1
  fi
  if ! [ -r $imagedir/post_install.ps1 ]; then
    echo -e "exit 0\r" > $imagedir/post_install.ps1
  fi
fi
touch $imagedir/packages.txt
PACKAGES="$(list-file-to-json packages $imagedir/packages.txt)"
touch $imagedir/files.txt
FILES="$(list-file-to-json files $imagedir/files.txt)"
if [ "$IMAGETYPE" = "ubuntu" ]; then
  touch $imagedir/repos.txt $imagedir/keys.txt
  REPOS="$(list-file-to-json repos $imagedir/repos.txt)"
  KEYS="$(list-file-to-json keys $imagedir/keys.txt)"
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]="$REPOS"
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]="$KEYS"
else
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]='{"repos": []}'
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]='{"keys": []}'
fi
if [ -n "$BASE_IMAGE_JOB" ]; then
  AMI=$(ndt get-images $BASE_IMAGE_JOB | head -1 | cut -d: -f1)
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=base_ami_id=$AMI
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=bake_userdata=win-userdata-unclean.txt.j2
else
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=base_ami_id=clean
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=bake_userdata=win-userdata.txt.j2
fi
if [ -n "$INSTANCE_TYPE" ]; then
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=instance_type=$INSTANCE_TYPE
else
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=instance_type=t2.medium
fi
if [ -n "$BAKE_TIMEOUT" ]; then
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=timeout_min=$BAKE_TIMEOUT
else
  extra_args[${#extra_args[@]}]=-e
  extra_args[${#extra_args[@]}]=timeout_min=55
fi

JOB=$(echo $JOB_NAME | sed 's/[^[:alnum:]_]/_/g' | tr '[:upper:]' '[:lower:]')
NAME="${JOB}_$BUILD_NUMBER"
AMI_TAG="$NAME"
echo "$AMI_TAG" > ami-tag.txt
echo "$NAME" > name.txt

export ANSIBLE_FORCE_COLOR=true
export ANSIBLE_HOST_KEY_CHECKING=false

if [ "$IMAGETYPE" = "windows" ]; then
  PLAYBOOK="$(n-include bake-win-image.yml)"
else
  PLAYBOOK="$(n-include bake-image.yml)"
fi
rm -f ami.properties ||:
cat > ansible.cfg << MARKER
[defaults]
retry_files_enabled = False
MARKER
if python -u $(which ansible-playbook) \
  -vvvv \
  --flush-cache \
  $PLAYBOOK \
  -e tools_version=$paramDeployToolsVersion \
  -e ami_tag=$AMI_TAG \
  -e ami_id_file=$(pwd -P)/ami-id.txt \
  -e job_name=$JOB \
  -e aws_key_name=$AWS_KEY_NAME \
  -e app_user=$APP_USER \
  -e app_home=$APP_HOME \
  -e build_number=$BUILD_NUMBER \
  -e private_subnet=$PRIVATE_SUBNET \
  -e "$PACKAGES" \
  -e "$FILES" \
  "${extra_args[@]}" \
  -e root_ami=$AMI \
  -e tstamp=$TSTAMP \
  -e aws_region=$REGION \
  -e ansible_ssh_user=$SSH_USER \
  -e imagedir="$(realpath "${imagedir}")" \
  -e subnet_id=$SUBNET \
  -e sg_id=$SECURITY_GROUP \
  -e amibake_instanceprofile=$AMIBAKE_INSTANCEPROFILE \
  -e pause_seconds=$PAUSE_SECONDS \
  -e "$PASSWD_ARG"; then

  echo "AMI_ID=$(cat ami-id.txt)" > ami.properties
  echo "NAME=$(cat name.txt)" >> ami.properties
  echo "WIN_PASSWD=$WIN_PASSWD" >> ami.properties
  echo "Baking complete."
  cat ami.properties
else
  echo "AMI baking failed"
  exit 1
fi

if [ -n "${SHARE_REGIONS}" ]; then
  echo "--------------------- Share to ${SHARE_REGIONS}"
  for region in ${SHARE_REGIONS//,/ } ; do
    var_region_accounts=REGION_${region//-/_}_ACCOUNTS
    if [ ! "${!var_region_accounts}" ]; then
      echo "Missing setting '${var_region_accounts}' in ${infrapropfile}"
      exit 1
    fi
    ndt share-to-another-region $(cat ami-id.txt) ${region} $(cat name.txt) ${!var_region_accounts}
  done
fi
echo "SUCCESS"
