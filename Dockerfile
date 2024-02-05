FROM python:3.11.7-bookworm
RUN mkdir -p /app
WORKDIR /app

# install poetry
RUN pip install --upgrade pip && \
    pip install poetry

# copy the poetry files \
COPY pyproject.toml poetry.lock /app/

# install the dependencies
RUN poetry install --no-root --only main


COPY ./llm_homology_api/ /app/llm_homology_api/
COPY ./scripts /app/scripts

# run the app
ARG VCS_REF
ARG GIT_COMMIT_HASH
ENV GIT_COMMIT_HASH=${VCS_REF:-${GIT_COMMIT_HASH:-"NO_GIT_COMMIT_PASSED_IN"}}
ENV VCS_REF=$GIT_COMMIT_HASH

WORKDIR /app/
#ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["/app/scripts/entrypoint.sh"]