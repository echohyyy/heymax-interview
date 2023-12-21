## Dependencies ##
1. Python3.8
2. Flask
3. Sqlite3
4. requests

## Before Setup ##
1. Make sure `libsqlite3-dev` and `pyhton3-dev` are installed system-wide.
2. The `wheel` Python package is required to build the `pysqlite3` package.

## Setup Instructions ##
1. Create a virtual env under project directory and activate the venv 
2. Install dependencies from requirements.txt (pip3 install)
3. Initiate the database **only** if the `database.db`` file doe
4. Run the server (python3 main.py)
5. Enter localhost:5000(http://127.0.0.1:5000) in the browser
6. Run unit tests by running test files in tests folder.

## Sample Users (please directly copy and paste)##
Account1:
name: sampleCustomer
password: sample
email: sampleCustomer@samplet.com
kind: customer

Account2:
name: sampleAdmin
password: sample
email: sampleAdmin@samplet.com
kind: admin

