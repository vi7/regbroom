import confuse
import argparse
from . import logger as l


def set_defaults(config):
    """Ensure defaults for all optional config options
    """
    for i in range(len(config['images'].get(list))):
      config['images'][i].get(dict).setdefault('release_ver_pattern', config['defaults']['release_ver_pattern'].get(str))
      config['images'][i].get(dict).setdefault('release_ver_keep', config['defaults']['release_ver_keep'].get(int))
      config['images'][i].get(dict).setdefault('dev_ver_pattern', config['defaults']['dev_ver_pattern'].get(str))
      config['images'][i].get(dict).setdefault('dev_ver_keep', config['defaults']['dev_ver_keep'].get(int))
      config['images'][i].get(dict).setdefault('force', False)
      config['images'][i].get(dict).setdefault('fail_on_error', True)

def load_config(args):
    """Load configuration from the provided config_local.yaml
    """
    config = confuse.Configuration('regbroom', __name__)
    config_path = 'config_local.yaml' if not args.config else args.config
    try:
        config.set_file(config_path, base_for_paths=True)
    except confuse.exceptions.ConfigReadError:
        l.log("\033[33mWARN: Config file '{}' not found. Using default search paths\033[0m".format(config_path))
    set_defaults(config)
    return config

def parse_args():
    """Parse command-line arguments
    """
    parser = argparse.ArgumentParser(prog='regbroom')
    parser.add_argument("-c", "--config", help="Path to the config file (default: %(default)s)",
                        metavar='CONFIGPATH',
                        default='config_local.yaml')
    args = parser.parse_args()
    return args
