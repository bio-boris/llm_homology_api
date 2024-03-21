import os
import pytest
from dotenv import load_dotenv

def run_tests():
    # Load .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    dotenv_file_name = "dev_kg02-p.env"  # Name of your .env file
    dotenv_file_full_path = os.path.join(script_dir, dotenv_file_name)
    if not os.path.isfile(dotenv_file_full_path):
        raise FileNotFoundError(f"File {dotenv_file_full_path} not found")
    load_dotenv(dotenv_file_full_path) or print(f"Error loading {dotenv_file_full_path}")

    # Set PYTHONPATH to include your project's directories, if necessary
    base_dir = os.path.join(script_dir, '..', '..', )  # Adjust this path to point to your project's base directory
    tests_dir = os.path.join(base_dir, 'tests')  # Path to the tests directory
    os.environ['PYTHONPATH'] = f"{os.environ.get('PYTHONPATH', '')}:{base_dir}"

    # Run pytest with coverage options and specify the path to the tests
    pytest_args = [
        tests_dir,  # Path to the tests
        f"--cov={base_dir}/llm_homology_api",  # Adjust this to your package name
        '--cov-report=xml',
        '--cov-report=term-missing',
        # '--cov-fail-under=80'  # Uncomment this if you want to enforce a minimum coverage
    ]

    # Execute pytest with the specified arguments
    return_code = pytest.main(pytest_args)

    # Check the return code to determine success or failure
    if return_code == 0:
        print("Pytest ran successfully!")
    else:
        print(f"Pytest exited with return code: {return_code}")

if __name__ == "__main__":
    run_tests()
