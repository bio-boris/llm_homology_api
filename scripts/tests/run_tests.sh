#!/bin/bash
# Run pytest with poetry
export VERSION='testing'
export AUTH_URL='https://ci.kbase.us/services/auth/api/V2/me'
# Must be set to '' for docs to work locally
export ROOT_PATH=''
export VCS_REF='no git commit set during build'
export PYTHONPATH=.:llm_homology_api:llm_homology_api/src
poetry run pytest --cov=llm_homology_api --cov-report=xml --cov-report=term-missing

#--cov-fail-under=80