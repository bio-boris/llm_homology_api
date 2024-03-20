##!/bin/bash
## Run the FastAPI app with poetry from the root directory
#. ./scripts/kg02-p.sh.env
#exec poetry run uvicorn --host 0.0.0.0 --port 5001 --factory llm_homology_api.src.factory:create_app --reload