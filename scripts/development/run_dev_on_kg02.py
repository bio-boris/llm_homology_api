#!/usr/bin/env python3
import os
import sys

import uvicorn
from dotenv import load_dotenv
from uvicorn.config import Config

# Determine the default .env filepath based on the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
default_env_fp = os.path.join(script_dir, ".env")

# Check if the .env file path is provided in command line arguments, else use the default
env_fp = sys.argv[1] if len(sys.argv) > 1 else default_env_fp

if __name__ == "__main__":
    # Attempt to load the specified .env file, fall back to the default if not found
    if not os.path.isfile(env_fp):
        print(f"Specified .env file {env_fp} not found, falling back to default .env")
        env_fp = default_env_fp
        if not os.path.isfile(env_fp):
            raise FileNotFoundError("Default .env file also not found. Please ensure an .env file is available.")

    load_dotenv(env_fp) or print(f"Error loading {env_fp}")
    print("Loaded .env file from ", env_fp)

    # Determine the reload directory based on the .env file's location (if needed)
    reload_dir = os.path.dirname(script_dir)
    base_dir = os.path.dirname(reload_dir)

    # Create a Uvicorn configuration object with the desired settings
    config = Config(
        "llm_homology_api.src.factory:create_app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        factory=True,
        log_level="debug",
        reload_dirs=[base_dir],
    )

    # Run Uvicorn with the custom configuration
    server = uvicorn.Server(config)
    server.run()
