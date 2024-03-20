import os
import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    # Construct the full path to the .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    dotenv_file_name = "dev_kg02-p.env"  # Name of your .env file
    dotenv_file_full_path = os.path.join(script_dir, dotenv_file_name)
    if not os.path.isfile(dotenv_file_full_path):
        raise FileNotFoundError(f"File {dotenv_file_full_path} not found")
    load_dotenv(dotenv_file_full_path) or print(f"Error loading {dotenv_file_full_path}")
    uvicorn.run("llm_homology_api.src.factory:create_app", host="0.0.0.0", port=5001, reload=True, factory=True)
