FROM python:3.10.0-alpine3.14

LABEL maintainer="vi7"

ARG WORKDIR=/regbroom
ARG CONFDIR=/root/.config/regbroom
ARG REGCTL_VER=0.3.9

RUN set -e \
  && wget -O /usr/local/bin/regctl https://github.com/regclient/regclient/releases/download/v${REGCTL_VER}/regctl-linux-amd64 \
  && chmod a+x /usr/local/bin/regctl

COPY ["docker/regctl_config.json", "/root/.regctl/config.json"]
COPY ["regbroom", "${WORKDIR}/regbroom/"]
COPY ["requirements.txt", "${WORKDIR}/"]
COPY ["config_local.yaml", "${CONFDIR}/config_example.yaml"]

WORKDIR ${WORKDIR}
RUN set -e \
  && pip install -r requirements.txt

VOLUME ${CONFDIR}

ENTRYPOINT ["python", "-m", "regbroom"]
