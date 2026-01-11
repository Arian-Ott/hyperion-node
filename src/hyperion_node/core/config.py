import os
import sys
import logging
from pathlib import Path
import configparser
from uuid import uuid7  # Changed to uuid4 for standard lib compatibility
from datetime import datetime
import click


class Config:
    def __init__(self):
        self.cnf_path = Path.home() / ".hyperion_node"
        self.cnf_file = self.cnf_path / "settings.cfg"
        self.cnf = configparser.ConfigParser()

        self.setup()
        self.load()

    def setup(self):
        """Creates the directory and default config if they don't exist."""
        if not self.cnf_path.exists():
            self.cnf_path.mkdir(parents=True, exist_ok=True)

        if not self.cnf_file.exists():
            self.cnf["hyperion-node"] = {
                "node-id": str(uuid7()),
                "created_at": datetime.now().isoformat(),
                "default_port": 2468,
            }
            self.flush()

    def load(self):
        """Reads the config file into the parser object."""
        if self.cnf_file.exists():
            with open(self.cnf_file, "r") as configfile:
                self.cnf.read_file(configfile)

    def flush(self):
        """Writes the current state of the parser to the file."""
        with open(self.cnf_file, "w") as configfile:
            self.cnf.write(configfile)

    def get_setting(self, section, key, fallback=None):
        try:
            return self.cnf.get(section, key)
        except configparser.NoSectionError:
            raise ValueError(f"Section '{section}' doesn't exist.")
        except configparser.NoOptionError:
            if fallback is None:
                raise ValueError(
                    f"Option '{key}' in section '{section}' does not exist."
                )
            return fallback

    def set_setting(self, section, key, value):
        """
        Fixed: Added 'value' argument.
        """
        if not self.cnf.has_section(section):
            self.cnf.add_section(section)

        self.cnf.set(section, key, str(value))
        self.flush()


cnf = Config()
