import base64
import datetime
import hashlib
import random
import string

from cryptography.fernet import Fernet
from django.conf import settings


def generate_fernet_key():
    hash = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(hash)


def encrypt_connection_string(conn_str):
    cipher_suite = Fernet(generate_fernet_key())
    return cipher_suite.encrypt(conn_str.encode())


def decrypt_connection_string(enc_conn_str):
    cipher_suite = Fernet(generate_fernet_key())
    return cipher_suite.decrypt(enc_conn_str).decode()


def generate_filename(reportname: str) -> str:
    wordlist = string.ascii_letters + string.digits
    salt = "".join(random.choice(wordlist) for _ in range(8))
    filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{reportname}-{salt}"
    return filename


def get_cache_key(data: dict, suffix: str) -> str:
    def make_hashable(item):
        key, value = item
        if isinstance(value, dict):
            return key, frozenset(value.items())
        return key, value

    hashable_items = map(make_hashable, data.items())
    return "report:" + str(hash(frozenset(hashable_items))) + f":{suffix}"
