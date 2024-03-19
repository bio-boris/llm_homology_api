#!/bin/bash
export AUTH_URL='https://ci.kbase.us/services/auth/api/V2/me'
# Must be set to '' for /docs endpoint to work locally
#export ROOT_PATH=''
export ROOT_PATH='/services/llm_homology_api'
export VCS_REF='no git commit set during build'
export PYTHONPATH=.:llm_homology_api:llm_homology_api/src
export VERSION='0.0.1'
export MODEL_DIR="/scratch/sprot/sprot_esm_650m_faiss"

exec poetry run uvicorn --host 0.0.0.0 --port 5001 --factory llm_homology_api.src.factory:create_app --reload
