# ======================================================================================================================
#        File:  settings.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""User settings management."""

# ======================================================================================================================
# Imports
# ----------------------------------------------------------------------------------------------------------------------
import os
from configparser import ConfigParser, NoSectionError, NoOptionError
import getpass
import logging
from typing import List, Tuple

import appdirs




# ======================================================================================================================
# Exceptions
# ----------------------------------------------------------------------------------------------------------------------
class InvalidSetting(Exception):
    """Raised when the provided key is not accepted/used by this application."""




# ======================================================================================================================
# Setting Class
# ----------------------------------------------------------------------------------------------------------------------
class Settings:
    def __init__(self):
        self.logger = logging.getLogger('settings')
        self.path = appdirs.user_data_dir('b', 'exsystems', roaming=True)
        self.file = os.path.join(self.path, 'settings.cfg')
        self.config = ConfigParser()
        self.defaults = {
            'general.editor': 'notepad' if os.name == 'nt' else 'nano',
            'general.dir': '.bugs',
            'general.user': getpass.getuser()
        }
        self.load()


# ----------------------------------------------------------------------------------------------------------------------
    @property
    def exists(self) -> bool:
        return os.path.exists(self.file)


# ----------------------------------------------------------------------------------------------------------------------
    def __enter__(self):
        return self


# ----------------------------------------------------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        self.store()


# ----------------------------------------------------------------------------------------------------------------------
    def load(self) -> None:
        if os.path.exists(self.file):
            with open(self.file, 'r') as handle:
                self.config.read_file(handle)
        keys = list(self.defaults.keys())
        for section in self.config.sections():
            for option in self.config.options(section):
                keys.append(f'{section}.{option}')
        keys = list(set(keys))
        self.logger.debug('Current settings:')
        for key in sorted(keys):
            self.logger.debug('- %s = "%s"', key, self.get(key))


# ----------------------------------------------------------------------------------------------------------------------
    def store(self) -> None:
        os.makedirs(self.path, exist_ok=True)
        with open(self.file, 'w') as handle:
            self.config.write(handle)


# ----------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _split_key(key: str) -> Tuple[str, str]:
        """Split a key name formatted as `section.option` into its constituent parts."""
        if '.' in key:
            return tuple(key.split('.', 1))
        return ('general', key)


# ----------------------------------------------------------------------------------------------------------------------
    def _validate_key(self, section: str, option: str) -> None:
        key = f'{section}.{option}'
        if key not in self.defaults.keys():
            raise InvalidSetting(f'Key "{key}" is not a valid setting.')
        return key


# ----------------------------------------------------------------------------------------------------------------------
    def set(self, key: str, value: str):
        section, option = self._split_key(key)
        self._validate_key(section, option)

        # Add the new section if it doesn't exist.
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, option, value)


# ----------------------------------------------------------------------------------------------------------------------
    def get(self, key: str) -> str:
        section, option = self._split_key(key)
        key = self._validate_key(section, option)
        try:
            return self.config.get(section, option)
        except (NoSectionError, NoOptionError):
            return self.defaults[key]


# ----------------------------------------------------------------------------------------------------------------------
    def unset(self, key: str, section: str = 'settings') -> bool:
        section, option = self._split_key(key)
        return self.config.remove_option(section, option)


# ----------------------------------------------------------------------------------------------------------------------
    def list(self) -> List[Tuple[str, str]]:
        return [(key, self.get(key)) for key in self.defaults.keys()]




# End of File
