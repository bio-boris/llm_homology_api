#!/bin/bash
export VERSION='testing'
export AUTH_URL='https://ci.kbase.us/services/auth/api/V2/me'
# Must be set to '' for /docs endpoint to work locally
export ROOT_PATH=''
export VCS_REF='no git commit set during build'
export PYTHONPATH=.:llm_homology_api:llm_homology_api/src
exec poetry run uvicorn --host 0.0.0.0 --port 5006 --factory llm_homology_api.src.factory:create_app --reload
