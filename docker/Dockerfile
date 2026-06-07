FROM python:3.14-slim-bookworm AS base_os
ARG GOSU_VERSION=1.19
ARG GOSU_SHA256=52c8749d0142edd234e9d6bd5237dff2d81e71f43537e2f4f66f75dd4b243dd0
ARG BUILD_DATE
ARG VERSION
ARG SOURCE_COMMIT

RUN set -x \
  && runtimeDeps=" \
    libmagic1 \
    libxml2 \
    libexpat1 \
    libpq-dev \
  " \
  && buildDeps=" \
    wget \
    gcc \
  " \
  && apt-get update && apt-get install -y --no-install-recommends ${buildDeps} ${runtimeDeps} \
  && rm -rf /var/lib/apt/lists/* \
  && wget --quiet -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
  && echo "$GOSU_SHA256 /usr/local/bin/gosu" | sha256sum --check --status \
  && chmod +x /usr/local/bin/gosu \
  && apt-get purge -y --auto-remove $buildDeps

RUN groupadd --gid 1024 unicef \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup unicef -q hope


FROM base_os AS builder
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG VERSION

RUN set -x \
    && buildDeps="build-essential \
    cmake \
    curl \
    gcc \
    libssl-dev \
    libxml2-dev \
    python3-dev \
    zlib1g-dev  \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv uwsgi

ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv

WORKDIR /app

COPY uv.lock README.md pyproject.toml /app/
COPY src /app/src/

RUN uv sync --python=/usr/local/bin/python \
    --python-preference=system \
    --no-dev --frozen


FROM builder AS tests
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG VERSION

LABEL distro="tests"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_ams.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv

WORKDIR /app

COPY uv.lock README.md pyproject.toml /app/
COPY src /app/src/

RUN uv sync --python=/usr/local/bin/python \
    --python-preference=system \
    --frozen --group dev


FROM builder AS production
ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_ams.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4

WORKDIR /app

COPY uv.lock README.md pyproject.toml /app/
COPY src /app/src/

RUN uv sync --python=/usr/local/bin/python \
    --python-preference=system \
    --no-dev --frozen


FROM base_os AS dist
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG BRANCH
ARG VERSION
ARG GITHUB_SERVER_URL
ARG GITHUB_REPOSITORY

ENV PATH=/venv/bin:/usr/local/bin/:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=hope_ams.config.settings \
    BUILD_DATE=$BUILD_DATE \
    SOURCE_COMMIT=$SOURCE_COMMIT \
    VERSION=$VERSION \
    BRANCH=$BRANCH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4

RUN cat > /RELEASE <<EOF
{"version": "$VERSION",
 "commit": "$SOURCE_COMMIT",
 "date": "$BUILD_DATE"}
EOF

WORKDIR /app

COPY docker/conf /conf/
COPY docker/bin/* /usr/local/bin/

COPY --chown=hope:unicef --from=production /venv /venv
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uv /usr/local/bin/

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]

LABEL maintainer="hope@unicef.org"
LABEL org.opencontainers.image.authors="hope@unicef.org"
LABEL org.opencontainers.image.description="HOPE Anomaly Management System"
LABEL org.opencontainers.image.documentation="https://github.com/unicef/hope-ams/"
LABEL org.opencontainers.image.title="HOPE AMS"
LABEL org.opencontainers.image.licenses="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/blob/${SOURCE_COMMIT:-master}/LICENSE"
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${SOURCE_COMMIT:-master}/"
LABEL org.opencontainers.image.url="https://hub.docker.com/repository/docker/unicef/hope-ams/tags/"
LABEL org.opencontainers.image.vendor="UNICEF"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"
