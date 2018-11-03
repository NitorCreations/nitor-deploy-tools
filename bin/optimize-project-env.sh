#!/bin/bash

sudo -H pip install -U nuitka
ENV_SCRIPT="$(dirname $(dirname $(n-include hook.sh)))/nitor-dt-load-project-env.py"
PROFILE_SCRIPT="$(dirname $(dirname $(n-include hook.sh)))/nitor-dt-enable-profile.py"
python -m nuitka --recurse-to=n_utils.project_util --follow-import-to=n_utils.profile_util $ENV_SCRIPT
python -m nuitka --follow-import-to=n_utils.profile_util $PROFILE_SCRIPT
sudo cp nitor-dt-load-project-env.bin $(which nitor-dt-load-project-env)
sudo cp nitor-dt-enable-profile.bin $(which nitor-dt-enable-profile)
