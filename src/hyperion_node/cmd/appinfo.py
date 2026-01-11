import click
from hyperion_node.assets.license_text import text
from hyperion_node.core.config import cnf
import logging


@click.command()
def info():
    try:
        node_id = cnf.get_setting("hyperion-node", "node-id")
        logging.info(f"Node ID: {node_id}")
    except ValueError as e:
        logging.error(e)


@click.command()
def license():
    click.echo_via_pager(text)
