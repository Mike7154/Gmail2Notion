import ruamel.yaml
import json
import urllib.parse
from datetime import datetime
import os
import cryptocode


def load_dict(file):
    f = open(file)
    url_dict = json.load(f)
    f.close()
    return url_dict


def write_dict(file, dict):
    with open(file, "w") as convert_file:
        convert_file.write(json.dumps(dict))

def create_json(json_file):
    if os.path.isfile(json_file) == False:
        dict = {}
        write_dict(json_file, dict)

def update_log(text):
    now = datetime.now()
    file = "logs.txt"
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    print(log_text)
    f = open(file, "a")
    f.write(log_text+'\n')
    f.close()

def load_setting(section, setting, settings_file = "settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    return data[section][setting]

def save_setting(section, setting, value, settings_file = "settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    data[section][setting] = value
    with open(settings, "w") as f:
        yaml.dump(data,f)

def load_all_settings(settings_file = "settings.yml"):
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        with open(settings_file) as fp:
            data = yaml.load(fp)
        return data

def save_all_settings(data, settings_file = "settings.yml"):
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        with open(settings_file, "w") as f:
            yaml.dump(data,f)
def hash(u,us,p,ps,h,hs, settings_file = "settings.yml"):
    data = load_all_settings(settings_file)
    if data[us][u] is None:
        data[us][u] = input("Please type your "+u+": ")
    if data[ps][p] is not None:
        data[hs][h] = cryptocode.encrypt(data[us][u], data[us][u])
        data[ps][p] = None
    if data[hs][h] is None:
        np = input("Please type your "+p+"(it will only be stored locally with basic encryption): ")
        data[hs][h] = cryptocode.encrypt(np, data[us][u])
        data[ps][p] = None

    pe = data[us][u]
    pp = cryptocode.decrypt(data[hs][h], pe)
    save_all_settings(data, settings_file)
    return cre(pe, pp, data[hs][h])

class cre:
    def __init__(self, u, p, h):
        self.u = u
        self.p = p
        self.h = h
