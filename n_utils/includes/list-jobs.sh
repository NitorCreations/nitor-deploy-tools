#!/bin/bash

if [ "$_ARGCOMPLETE" ]; then
  exit 0
fi
usage() {
  echo "usage: ndt list-jobs  [-h]" >&2
  echo "" >&2
  echo "List jobs that should be created in jenkins for the current repository." >&2
  echo "This includes all branches in the current repository." >&2
  echo "" >&2
  echo "optional arguments:" >&2
  echo "  -h, --help  show this help message and exit" >&2  exit 1
}
if [ "$1" = "--help" -o "$1" = "-h" ]; then
  usage
fi

source $(n-include autocomplete-helpers.sh)

buildable_branches() {
  for BRANCH in $(git branch -r | grep -v origin/HEAD | cut -d/ -f 2-); do
    checkout_branch $BRANCH
  done
}
list_jobs() {
  mkdir -p job-properties
  for GIT_BRANCH in $(buildable_branches); do
    cd "$GIT_BRANCH-checkout"
    for IMAGE_DIR in $(get_bakeable_images); do
      job_properties $GIT_BRANCH $IMAGE_DIR > "../job-properties/image-$GIT_BRANCH-$IMAGE_DIR.properties"
      echo "$IMAGE_DIR:$GIT_BRANCH:image:-"
    done
    for IMAGE_DIR in $(get_stack_dirs); do
      for STACK in $(get_stacks $IMAGE_DIR); do
        job_properties $GIT_BRANCH $IMAGE_DIR -s $STACK > "../job-properties/stack-$GIT_BRANCH-$IMAGE_DIR-$STACK.properties"
        echo "$IMAGE_DIR:$GIT_BRANCH:stack:$STACK"
      done
      for DOCKER in $(get_dockers $IMAGE_DIR); do
         job_properties $GIT_BRANCH $IMAGE_DIR -d $DOCKER > "../job-properties/docker-$GIT_BRANCH-$IMAGE_DIR-$DOCKER.properties"
        echo "$IMAGE_DIR:$GIT_BRANCH:docker:$DOCKER"
      done
      for SERVERLESS in $(get_serverless $IMAGE_DIR); do
         job_properties $GIT_BRANCH $IMAGE_DIR -s $SERVERLESS > "../job-properties/docker-$GIT_BRANCH-$IMAGE_DIR-$DOCKER.properties"
        echo "$IMAGE_DIR:$GIT_BRANCH:serverless:$SERVERLESS"
      done
    done
    cd ..
    rm -rf "$GIT_BRANCH-checkout"
  done
}
list_jobs | sort
