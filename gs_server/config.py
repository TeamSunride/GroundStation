import yaml


class ConfigNotFoundError(Exception):
    pass


with open("python_config.yml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


def conf(*keys):
    item = None
    for key in keys:
        if not item:
            item = config.get(key, None)
        else:
            item = item.get(key, None)
    if item is not None:
        return item
    else:
        raise ConfigNotFoundError("Could not find the following in config.yml: " + " → ".join(keys))
