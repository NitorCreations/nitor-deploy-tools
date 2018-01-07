#!/bin/bash

if [ "$_ARGCOMPLETE" ]; then
  unset _ARGCOMPLETE
  source $(n-include autocomplete-helpers.sh)
  # Handle command completion executions
  COMP_WORDS=( $COMP_LINE )
  IMAGE_DIR=${COMP_WORDS[2]}
  STACK=${COMP_WORDS[3]}
  IMAGE=$(echo $IMAGE_DIR| tr "-" "_")
  case $COMP_CWORD in
    2)
      compgen -W "$(get_stack_dirs)" -- $COMP_CUR
      ;;
    3)
      compgen -W "$(get_stacks $IMAGE_DIR)" -- $COMP_CUR
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi

source $(n-include autocomplete-helpers.sh)

COMPONENT=$1
STACK=$2

[ "$GIT_BRANCH" ] || GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [ -d $COMPONENT/image ]; then
  echo "You can bake the component image by running 'ndt bake-image $COMPONENT'"
  eval $(job_properties $GIT_BRANCH $1)
  AMI_SUFFIX=" \"\" $JENKINS_JOB_PREFIX-$1-bake"
fi

PREFIX=$COMPONENT/docker-
if ls $COMPONENT/docker-* > /dev/null 2>&1; then
  for DOCKER in $COMPONENT/docker-*; do
    DOCKER_NAME=${DOCKER#$PREFIX}
    echo "You can bake the $DOCKER_NAME docker image by running 'ndt bake-docker $COMPONENT $DOCKER_NAME'"
  done
fi

echo "You can deploy the stack $STACK by running 'ndt deploy-stack $COMPONENT $STACK$AMI_SUFFIX'"