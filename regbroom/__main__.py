#
# Docker Registry Broom
#
# Requires 'regctl' utility to be present on the host
# 'regctl' and its docs could be found here https://github.com/regclient/regclient
#

import yaml
from . import regbroom as rb
from . import logger as l
from . import config as conf


args = conf.parse_args()
config = conf.load_config(args)
l.set_config(config)
if config['dryrun']:
  l.log("\033[33mDRY RUN mode is ENABLED. No real cleanup will be performed\033[0m")
l.log_debug("Running with the configuration:\n{}".format(config.dump()))

rb.set_config(config)
rb.sweep()
