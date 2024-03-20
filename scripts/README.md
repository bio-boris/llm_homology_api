# All scripts expected to be run from the root of the repository

# Development Scripts

### Developing on kg02-p
#### Example ssh config file

* SSH config setup
```bash
Host bastion
   Hostname jump_host
   User <username>
Host kg02-p
   Hostname kg02-p
   User <username>
   ProxyJump bastion
```
### Remote Interpreter Setup

#### Python environment setup
* python3 -m venv venv
* source venv/bin/activate
* poetry update

#### Set up your remote interpreter
* Choose `~/llm_homology/venv/bin/python` as your remote interpreter
* Setup path mappings

#### Run the development environment
* Run `scripts/run_dev_kg02_p_for_pycharm.py`
* You can set breakpoints and run the code in the remote interpreter