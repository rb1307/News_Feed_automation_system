import json


def output_json(path=None, file_name=None, data=None):
    with open(path+file_name, mode='w') as f:
        json.dump(data, f)
    return 0
