#!/bin/bash

if [ "$_ARGCOMPLETE" ]; then
  exit 0
fi

source $(n-include autocomplete-helpers.sh)

buildable_branches() {
  for BRANCH in $(git branch -r | grep -v origin/HEAD | cut -d/ -f 2-); do
    mkdir -p "$BRANCH-checkout" > /dev/null 2>&1
    git --git-dir ../.git -C "$BRANCH-checkout" checkout "$BRANCH" -- . > /dev/null 2>&1
    if [ -r "$BRANCH-checkout/infra-$BRANCH.properties" ]; then
      echo $BRANCH
    else
      rm -rf "$BRANCH-checkout" > /dev/null 2>&1
    fi
  done
}
list_jobs() {
  for GIT_BRANCH in $(buildable_branches); do 
    cd "$GIT_BRANCH-checkout"
    for IMAGE_DIR in $(get_bakeable_images); do
      source source_infra_properties.sh $IMAGE_DIR
      IMAGE=$(echo $IMAGE_DIR| tr "-" "_")
      echo "$GIT_BRANCH:image:$IMAGE_DIR:${JENKINS_JOB_PREFIX}_${IMAGE}_bake"
    done
    for IMAGE_DIR in $(get_stack_dirs); do
      IMAGE=$(echo $IMAGE_DIR| tr "-" "_")
      for STACK in $(get_stacks $IMAGE_DIR); do
        echo "$GIT_BRANCH:stack:$STACK:$IMAGE_DIR:${JENKINS_JOB_PREFIX}_${IMAGE}_${STACK}_deploy"
      done
    done
    cd ..
    rm -rf "$GIT_BRANCH-checkout"
  done
}
list_jobs | sort
