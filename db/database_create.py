import sqlite3
import os
import sys
import os.path
import re
import passwordhash

if os.path.isfile("database.db"):
    try:
        os.unlink("database.db")
    except OSError:
        input("Database is already open in another program and cant be changed! "
              "Press enter to close.")
        sys.exit()
conn = sqlite3.connect("database.db")
cur = conn.cursor()
with open("init.sql") as init:
    cur.executescript(init.read())
with open("dummy_data.sql") as data:
    sqlfile = data.read()
    hashed = re.sub(
        r"HASH\([\"'](.+?)[\"']\)",
        lambda x: '"{}"'.format(
            passwordhash.hash_password(x.group(1)).decode("ascii")
        ),
        sqlfile
    )
    cur.executescript(hashed)
cur.close()
conn.close()
