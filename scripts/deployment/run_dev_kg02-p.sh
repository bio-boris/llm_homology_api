###!/bin/bash
## Run the FastAPI app with poetry from the root directory
#
#export PYTHONPATH=.:llm_homology_api:llm_homology_api/src
#. ./scripts/deployment/deploy_kg02-p.env
#exec poetry run uvicorn --host 0.0.0.0 --port 5001 --factory llm_homology_api.src.factory:create_app --reload