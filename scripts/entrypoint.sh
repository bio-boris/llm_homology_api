#!/bin/bash
export PYTHONPATH=.:llm_homology_api:llm_homology_api/src
exec poetry run uvicorn --host 0.0.0.0 --port 5000 --factory llm_homology_api.src.factory:create_app