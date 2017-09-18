#/bin/bash -x

# Make sure we get logging
if grep cloud-init-output.log /etc/cloud/cloud.cfg.d/05_logging.cfg > /dev/null ; then
  echo "output: {all: '| tee -a /var/log/cloud-init-output.log'}" >> /etc/cloud/cloud.cfg.d/05_logging.cfg
fi
