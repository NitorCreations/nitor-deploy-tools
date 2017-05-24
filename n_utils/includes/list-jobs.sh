#!/bin/bash

if [ "$_ARGCOMPLETE" ]; then
  exit 0
fi
IGNORE_PROPS='^(BASH.*|DIR|TERM|.?UID|_|GROUPS|IFS|OPTERR|OPTIND|SHELL|PIPE|PS4|PPID|SHLVL|PATH|PWD|OSTYPE|HOST(NAME|TYPE)|MACHTYPE|SHELLOPTS|DIRSTACK|PIPESTATUS)='
source $(n-include autocomplete-helpers.sh)
#If region not set in infra files, get the region of the instance or from env
[ "$REGION" ] || REGION=$(ec2-region)
# Same logic as above for account id
[ "$ACCOUNT_ID" ] || ACCOUNT_ID=$(account-id)

buildable_branches() {
  for BRANCH in $(git branch -r | grep -v origin/HEAD | cut -d/ -f 2-); do
    mkdir -p "$BRANCH-checkout" > /dev/null 2>&1
    git archive "origin/$BRANCH" | tar -xC "$BRANCH-checkout" > /dev/null 2>&1
    if [ -r "infra-$BRANCH.properties" ]; then
      echo $BRANCH
    else
      rm -rf "$BRANCH-checkout" > /dev/null 2>&1
    fi
  done
}
list_jobs() {
  mkdir -p job-properties
  for GIT_BRANCH in $(buildable_branches); do
    cd "$GIT_BRANCH-checkout"
    for IMAGE_DIR in $(get_bakeable_images); do
      env -i REGION="$REGION" ACCOUNT_ID="$ACCOUNT_ID" GIT_BRANCH="$GIT_BRANCH" \
        bash -c "source source_infra_properties.sh $IMAGE_DIR ; set" | \
        egrep -v "$IGNORE_PROPS" > "../job-properties/image-$GIT_BRANCH-$IMAGE_DIR.properties"
      echo "$IMAGE_DIR:$GIT_BRANCH:image:-"
    done
    for IMAGE_DIR in $(get_stack_dirs); do
      for STACK in $(get_stacks $IMAGE_DIR); do
        env -i REGION="$REGION" ACCOUNT_ID="$ACCOUNT_ID" GIT_BRANCH="$GIT_BRANCH" \
          bash -c "source source_infra_properties.sh $IMAGE_DIR $STACK; set" | \
          egrep -v "$IGNORE_PROPS" > "../job-properties/stack-$GIT_BRANCH-$IMAGE_DIR-$STACK.properties"
        echo "$IMAGE_DIR:$GIT_BRANCH:stack:$STACK"
      done
    done
    cd ..
    rm -rf "$GIT_BRANCH-checkout"
  done
}
list_jobs | sort
