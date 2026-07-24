import json

from default import PATH

file_name = PATH["temp_config"] / "settings.json"


def load_config():
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            result = json.load(f)
    except FileNotFoundError:
        result = {}

    return result


def add_entry(key, value):
    result = load_config()
    if result:
        with open(file_name, mode="r", encoding="utf-8") as f:
            result = json.load(f)

        result[key] = value

        with open(file_name, mode="w", encoding="utf-8") as f:
            json.dump(result, f)

    else:
        entry = {}
        entry[key] = value
        with open(file_name, mode="w", encoding="utf-8") as f:
            json.dump(entry, f)
