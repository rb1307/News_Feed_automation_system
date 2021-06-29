import json
import pandas as pd
from Modules.CustomErrors import *


def input_excel(file_name=None, path=None):
    input_data = pd.DataFrame()
    absolute_path = path + "/" + file_name
    try:
        input_data = pd.read_excel(absolute_path)
        return input_data
    except Exception as e:
        print(e)
        return input_data


def input_json(path=None, file_name=None):
    file_name = path + '/' + file_name
    try:
        with open(file_name, mode='r') as f:
            data = json.load(f)
            return data
    except Exception:
        raise InputDataError()


def get_db_credentials(path=None, file_name=None):
    file_name = path + '/' + file_name
    try:
        with open(file_name, mode='r') as f:
            data = json.load(f)
        return data.get("username"), data.get("password")
    except Exception:
        raise InputDataError()
