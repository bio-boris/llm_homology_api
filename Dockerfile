FROM python:3.10
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

ARG VCS_REF=NO_GIT_COMMIT_PROVIDED_DURING_BUILD
ARG VERSION=NO_POETRY_VERSION_PROVIDED_DURING_BUILD
ENV VCS_REF=$VCS_REF
ENV VERSION=$VERSION


WORKDIR /app/
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
