#!/bin/bash


#jinja llm_homology_api.toml.jinja -X "^KBCOLL_" > llm_homology_api.toml

# FastAPI recommends running a single process service per docker container instance as below,
# and scaling via adding more containers. If we need to run multiple processes, use guvicorn as
# a process manager as described in the FastAPI docs
#exec uvicorn --host 0.0.0.0 --port 5000 --factory llm_homology_api.src.app:create_app


PYTHONPATH=. exec uvicorn --host 0.0.0.0 --port 5000 --factory llm_homology_api.src.factory:create_app