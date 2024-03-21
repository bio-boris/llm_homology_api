#!/usr/bin/env python3
import os
import uvicorn
from dotenv import load_dotenv
from uvicorn.config import Config

if __name__ == "__main__":
    # Construct the full path to the .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    dotenv_file_name = "deploy_kg02-p.env"  # Name of your .env file
    dotenv_file_full_path = os.path.join(script_dir, dotenv_file_name)
    if not os.path.isfile(dotenv_file_full_path):
        raise FileNotFoundError(f"File {dotenv_file_full_path} not found")
    load_dotenv(dotenv_file_full_path) or print(f"Error loading {dotenv_file_full_path}")

    # Specify the directory to watch for changes, one level up from the script directory
    reload_dir = os.path.dirname(script_dir)
    base_dir = os.path.dirname(reload_dir)

    # Create a Uvicorn configuration object with the desired settings
    config = Config("llm_homology_api.src.factory:create_app", host="0.0.0.0", port=5001, factory=True, log_level="debug",
                    reload_dirs=[base_dir])

    # Run Uvicorn with the custom configuration
    server = uvicorn.Server(config)
    server.run()
