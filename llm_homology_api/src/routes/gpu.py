from pprint import pprint

print("invidia gpu")
import subprocess

print(subprocess.run(["nvidia-smi"], capture_output=True).stdout)
