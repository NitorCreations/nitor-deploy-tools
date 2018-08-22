#!/bin/bash

sudo -H pip install -U nuitka
ENV_SCRIPT="$(dirname $(dirname $(n-include hook.sh)))/nitor-dt-load-project-env.py"
python -m nuitka --recurse-to=n_utils.project_util $ENV_SCRIPT
sudo cp nitor-dt-load-project-env.exe $(which nitor-dt-load-project-env)
