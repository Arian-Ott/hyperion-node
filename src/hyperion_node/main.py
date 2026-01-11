import click
from hyperion_node.core.config import cnf
from hyperion_node.cmd.server import server
from hyperion_node.cmd.appinfo import info, license
from hyperion_node.assets.license_text import text
import logging
from pathlib import Path


@click.group(epilog="Copyright (C) 2026 Dein Name. Licensed under GPLv3.")
def cli():
    pass


cli.add_command(info)
cli.add_command(license)

cli.add_command(server)
