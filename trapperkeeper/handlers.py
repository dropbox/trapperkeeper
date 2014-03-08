
import yaml
import copy
import oid_translate
import collections


class Handlers(object):

    def __init__(self, defaults=None, traphandlers=None):
        self._defaults = defaults or {}
        self._traphandlers = traphandlers or {}

    def __getitem__(self, index):
        if not index.startswith("."):
            index = "." + index
        return self._traphandlers.get(index, self._defaults)

    @staticmethod
    def update(original, update_from):
        for key, value in update_from.iteritems():
            if isinstance(value, collections.Mapping):
                original[key] = Handlers.update(original.get(key, {}), value)
            else:
                original[key] = update_from[key]
        return original

    @staticmethod
    def from_file(config_filename):
        with open(config_filename) as config_file:
            config = yaml.safe_load(config_file)

        defaults = {
            "expiration": "15m",
            "mail": {
                "subject": "$(hostname)s $(trap_name)s",
            },
            "blackhole": False,
        }
        Handlers.update(defaults, config.get("defaults", {}))

        templates = config.get("templates", {})
        traphandlers = {}

        for oid, config in config.get("traphandlers", {}).iteritems():
            full_config = copy.deepcopy(defaults)
            if "use" in config:
                template = config.pop("use")
                Handlers.update(full_config, copy.deepcopy(
                    templates.get(template, {})
                ))
            Handlers.update(full_config, config)
            oid = oid_translate.translate(oid, oid_translate.OID_OUTPUT_NUMERIC)
            traphandlers[oid] = full_config

        return Handlers(defaults, traphandlers)
