import hashlib
import binascii
import os.path

if os.path.isfile("salt.txt"):
    with open("salt.txt") as salt_file:
        salt = salt_file.read().strip().encode("ascii")
else:
    salt = b"xisH44wduw3VWC8TBiRK"

def hash_password(password):
    bin_password = password.encode("ascii")
    dk = hashlib.pbkdf2_hmac("sha256", bin_password, salt, 100000)
    return binascii.hexlify(dk)
