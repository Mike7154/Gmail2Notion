import ruamel.yaml
import json
import os
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def load_dict(file: str) -> dict:
    with open(file) as f:
        return json.load(f)


def write_dict(file: str, data: dict) -> None:
    with open(file, "w") as convert_file:
        json.dump(data, convert_file)


def create_json(json_file: str) -> None:
    if not os.path.isfile(json_file):
        write_dict(json_file, {})


def update_log(text: str) -> None:
    now = datetime.now()
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = f"{timestr} : {text}"
    print(log_text)
    with open("logs.txt", "a") as f:
        f.write(log_text + '\n')


def load_setting(section: str, setting: str, settings_file: str = "settings.yml") -> str:
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    return data[section][setting]


def save_setting(section: str, setting: str, value: str, settings_file: str = "settings.yml") -> None:
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    data[section][setting] = value
    with open(settings_file, "w") as f:
        yaml.dump(data, f)


def load_all_settings(settings_file: str = "settings.yml") -> dict:
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        return yaml.load(fp)


def save_all_settings(data: dict, settings_file: str = "settings.yml") -> None:
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file, "w") as f:
        yaml.dump(data, f)


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt(password: str, plaintext: str) -> dict:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return {
        'salt': salt,
        'iv': iv,
        'ciphertext': ciphertext,
        'tag': encryptor.tag
    }


def decrypt(password: str, encrypted_data: dict) -> str:
    key = derive_key(password, encrypted_data['salt'])
    cipher = Cipher(algorithms.AES(key), modes.GCM(encrypted_data['iv'], encrypted_data['tag']), backend=default_backend())
    decryptor = cipher.decryptor()
    return (decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()).decode()


def hash(u: str, us: str, p: str, ps: str, h: str, hs: str, settings_file: str = "settings.yml") -> 'Credentials':
    data = load_all_settings(settings_file)
    if data[us].get(u) is None:
        data[us][u] = input(f"Please type your {u}: ")
    if data[ps].get(p) is not None:
        encrypted_data = encrypt(data[us][u], data[us][u])
        data[hs][h] = encrypted_data
        data[ps][p] = None
    if data[hs].get(h) is None:
        np = input(f"Please type your {p} (it will only be stored locally with basic encryption): ")
        encrypted_data = encrypt(np, data[us][u])
        data[hs][h] = encrypted_data
        data[ps][p] = None

    pe = data[us][u]
    pp = decrypt(data[us][u], data[hs][h])
    save_all_settings(data, settings_file)
    return Credentials(pe, pp, data[hs][h])


class Credentials:
    def __init__(self, username: str, password: str, hash: dict):
        self.username = username
        self.password = password
        self.hash = hash
