[![CircleCI](https://circleci.com/gh/vi7/regbroom/tree/master.svg?style=svg)](https://circleci.com/gh/vi7/regbroom/tree/master)

Docker Registry Broom - make your registry clean again!
============================

Regbroom tool cleans up Docker Registry image tags by specified release (e.g. X.Y.Z) and development version (e.g. X.Y.Z-bla.1) patterns keeping only specified amount of the most recently published tags.

Dev version tag keep logic is the following: keep specified in the config amount of dev tags per kept release tag (substring match) OR just keep specified amount of dev tags from the whole list of tags matching dev pattern if no release tags found and `force` flag is specified in the repo config.

> **IMPORTANT** Tool relies on 'last updated' sorting of the Docker Registry API, thus Regbroom might not work as you expect if your Registry API sorts the list of tags differently.
> For example Docker HUB API seems to sort in lexicographic order which won't be suitable for the Regbroom

Table of contents
-----------------

- [Requirements](#requirements)
- [Usage](#usage)
- [Configuration](#configuration)
  * [Config examples](#config-examples)
- [Advanced configuration](#advanced-configuration)
  * [Using non HTTPS/TLS Docker registries](#using-non-https-tls-docker-registries)
- [Development](#development)
  * [Releasing the image](#releasing-the-image)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


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

**Running with Docker**

Prepare Regbroom `config.yaml` (see details in the [Configuration](#configuration) section) and then run:
```bash
docker run --rm \
  -v /path/to/regbroom/config.yaml:/root/.config/regbroom/config.yaml
  vi7al/regbroom
```


Configuration
-------------

If running directly from this repo default configuration will be loaded from the provided [config_local.yaml](./config_local.yaml)

Run Regbroom like follows to override the config:
```bash
python -m regbroom --config /path/to/the/config.yaml
```

> `Confuse` Python module used to handle Regbroom config has also some predefined search paths for the `config.yaml`.
> See [https://confuse.readthedocs.io/en/latest/usage.html#search-paths](https://confuse.readthedocs.io/en/latest/usage.html#search-paths) for the details

### Config options and examples

See [config_local.yaml](./config_local.yaml) for options description and some handy configuration examples


Advanced configuration
----------------------

### Using non HTTPS/TLS Docker registries

To allow Regbroom to work with non HTTPS/TLS Docker registries configure `regctl` tool accordingly using `regctl registry set <registry> --tls disabled`

**Dockerized Regbroom**

By default Regbroom Docker image comes with the example of insecure registries config for the `regctl` tool. This could be found in the [docker/regctl_config.json](docker/regctl_config.json)

If you need to tell regctl to not use HTTPS for some other real registries this could be achieved via following ways:
- permanent way: change mentioned json config and build custom Regbroom Docker image
- runtime way: prepare your custom regctl `config.json` using `regctl registry set <registry> --tls disabled` and mount this custom config as an additional volume:
  ```bash
  docker run --rm \
    -v /etc/regbroom:/root/.config/regbroom \  # Regbroom config volume
    -v "$HOME"/.regctl/config.json:/root/.regctl/config.json \  # custom regctl config.json
    vi7al/regbroom
  ```

Development
-----------

### Releasing the image

Change whatever is needed

Bump the version in the [ci/build.env](ci/build.env)

Create Merge Request and add maintainers from [Dockerfile](Dockerfile) as reviewers

After MR is reviewed, tested and merged to the master run:
```bash
git checkout master && git pull --rebase
make release
```

> Run `make help` to see all the available tasks


TODO:
-----

- CI: run check_version.sh for PRs
- CI: functional tests by parsing regbroom stdout for expected messages
- Connect to Dockerhub for images building
