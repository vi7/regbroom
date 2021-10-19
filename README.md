Docker Registry Broom - make your registry clean again!
=======================================================

Tool cleans up Docker Registry image tags by specified release (e.g. X.Y.Z) and development version (e.g. X.Y.Z-bla.1) patterns keeping only specified amount of the most recently published tags.

Dev versions to keep are chosen from the dev tags matching corresponding kept release tags (substring match)


Requirements
------------

Python 3

`regctl` tool from https://github.com/regclient/regclient (used for the low-level API calls to the Docker Registry)


Usage
-----

Activate Python 3 virtualenv and install required packages via `pip install -r requirements.txt`

Check if regbroom works by printing the help message:
```bash
python -m regbroom --help
```

Run regbroom with the default configuration.
```bash
python -m regbroom
```

> Dry run mode is enabled in the default [config_local.yaml](./config_local.yaml) so the command above will not perform any real cleanup.

TODO: pack the tool as Docker image to avoid preparation steps above altogether

Configuration
-------------

Default configuration for the tool it loaded from the provided [config_local.yaml](./config_local.yaml) and could be overridden via cli like that:
```bash
python -m regbroom --config /path/to/the/config_local.yaml
```

> `Confuse` Python module used to handle config files has also some predefined search paths for the `config_local.yaml`.
> See [https://confuse.readthedocs.io/en/latest/usage.html#search-paths](https://confuse.readthedocs.io/en/latest/usage.html#search-paths) for the details

### Config examples

See [config_local.yaml](./config_local.yaml) for some handy configuration examples
