FROM python:3.10-slim-bullseye

ARG APP_USER=appuser

RUN apt-get -q update && \
    apt-get -qy install postgresql-client \
                        procps \
                        htop \
                        gcc \
                        libpq-dev \
                        netcat \
                        gunicorn3 &&\
    rm -rf /var/lib/apt/lists/* && \
    export PATH=$(pg_config --bindir):$PATH

RUN groupadd -r ${APP_USER} && useradd --no-log-init --create-home -u 1000 -r -g ${APP_USER} ${APP_USER}

ARG APP_DIR=/home/${APP_USER}/project/
RUN echo $APP_DIR && mkdir ${APP_DIR} && chown ${APP_USER}:${APP_USER} ${APP_DIR}

COPY --chown=${APP_USER}:${APP_USER} ./services/backend/requirements.txt ${APP_DIR}

RUN set -ex &&\
    pip install --upgrade pip && \
    pip install --no-cache-dir -r ${APP_DIR}requirements.txt

COPY --chown=${APP_USER}:${APP_USER} ./services/backend/service ${APP_DIR}service

# Setting build timestamp
RUN date '+%F-%H:%M:%S' > build.timestamp

USER ${APP_USER}:${APP_USER}

WORKDIR ${APP_DIR}service
