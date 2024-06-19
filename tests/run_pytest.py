#!/usr/bin/env python
import os
import sys
import pytest
from dotenv import load_dotenv

# This is a helper script to run pytest with the necessary environment variables loaded.
# (venv) bsadkhin@kg02-p:~/llm_homology_api$ poetry run python tests/run_pytest.py

# Load environment variables from .env file
if os.path.exists("tests/.env"):
    load_dotenv("tests/.env")
else:
    print("Couldnt find tests/.env file")
    if os.path.exists(".env"):
        load_dotenv(".env")
    else:
        print("Couldnt find .env file")
        sys.exit(1)



# Add paths to sys.path
sys.path.insert(0, ".")
sys.path.insert(0, "llm_homology_api")
sys.path.insert(0, "llm_homology_api/src")

# Run pytest
pytest_args = [
    "--cov=llm_homology_api",  # Path to the module you want to measure coverage for
    "--cov-report=html",       # Generate an HTML report
    "--cov-report=term"        # Show coverage summary in the terminal
]
pytest.main(pytest_args)

