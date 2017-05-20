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
      if ! [ "$JENKINS_JOB_NAME" ]; then
        JENKINS_JOB_NAME="${JENKINS_JOB_PREFIX}-${IMAGE_DIR}-bake"
      fi
      if ! [ "$SKIP_BAKE_JOB" = "y" ]; then
        if ! [ "$MANUAL_DEPLOY" = "y" ]; then
          MANUAL_DEPLOY="n"
        fi
        echo "$GIT_BRANCH:image:$IMAGE_DIR:$MANUAL_DEPLOY:$JENKINS_JOB_PREFIX:$JENKINS_JOB_NAME"
      fi
    done
    for IMAGE_DIR in $(get_stack_dirs); do
      for STACK in $(get_stacks $IMAGE_DIR); do
        if ! [ "$JENKINS_JOB_NAME" ]; then
          JENKINS_JOB_NAME="${JENKINS_JOB_PREFIX}-${IMAGE_DIR}-${STACK}-deploy"
        fi
        source source_infra_properties.sh $IMAGE_DIR $STACK
        if ! [ "$SKIP_DEPLOY_JOB" = "y" ]; then
          echo "$GIT_BRANCH:stack:$IMAGE_DIR:$STACK:$JENKINS_JOB_PREFIX:$JENKINS_JOB_NAME"
        fi
      done
    done
    cd ..
    rm -rf "$GIT_BRANCH-checkout"
  done
}
list_jobs | sort
