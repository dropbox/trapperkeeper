import pytz
import yaml

settings = {
    "debug": False,
    "database": None,
    "num_processes": 1,
    "port": 8888,
    "timezone": pytz.timezone("UTC"),
}

def update_from_config(filename):
    with open(filename) as config:
        data = yaml.safe_load(config.read())

    for key, value in data.iteritems():
        key = key.lower()

        if key not in settings:
            continue

        if key == "timezone":
            try:
                settings["timezone"] = pytz.timezone(value)
            except pytz.exceptions.UnknownTimeZoneError:
                continue
        else:
            settings[key] = value
