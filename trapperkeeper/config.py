import collections
import copy
import logging
from oid_translate import ObjectId
import yaml

from trapperkeeper.exceptions import ConfigError


class Config(object):

    REQUIRED = set(["database"])

    def __init__(self, config, handlers):
        self._config = config
        self.handlers = handlers

        for required in Config.REQUIRED:
            if required not in self:
                raise ConfigError("Invalid Config. Missing %s" % required)

    def __getitem__(self, index):
        return self._config[index]

    def __contains__(self, elem):
        return elem in self._config

    @staticmethod
    def from_file(config_filename, handlers=True):
        with open(config_filename) as config_file:
            config = yaml.safe_load(config_file)
        if handlers:
            _handlers = Handlers.from_dict(config)
        else:
            _handlers = None
        return Config(config.get("config", {}), _handlers)


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
    def from_dict(config):
        defaults = {
            "expiration": "15m",
            "mail": {
                "subject": "%(hostname)s %(trap_name)s",
            },
            "severity": "warning",
            "blackhole": False,
            "mail_on_duplicate": False,
        }
        Handlers.update(defaults, config.get("defaults", {}))

        templates = config.get("templates", {})
        traphandlers = {}

        for name, config in config.get("traphandlers", {}).iteritems():
            full_config = copy.deepcopy(defaults)
            if "use" in config:
                template = config.pop("use")
                Handlers.update(full_config, copy.deepcopy(
                    templates.get(template, {})
                ))
            Handlers.update(full_config, config)
            try:
                oid = ObjectId(name).oid
                traphandlers[oid] = full_config
            except ValueError, err:
                logging.warning("Failed to process traphandler %s: %s", name, err)

        return Handlers(defaults, traphandlers)
