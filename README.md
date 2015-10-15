# Lyar
NCSS 2015 Group 2's project. A web version of the classic game "Two Truths, One Lie."

## Running the server
Prerequisites:
* Python **3.4** (Tornado does not support Python 2, and we are using `hashlib.pbkdf2_hmac` which was first added in 3.4.)

First, run 'db\database_create.py' to create a local database on your first time using it. 
From then on, simply run `run.py` and the server should start serving at `localhost:8888`.

## Contributors
Please see CONTRIBUTORS.md. There were many people in the original team, and listing them here would be too long.
