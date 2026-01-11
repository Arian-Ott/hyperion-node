import click
import sys
import os
import asyncio
import websockets
import platform
import subprocess
import logging
from pathlib import Path

# Vorhandene Imports
from hyperion_node.core.config import cnf
from hyperion_node.cmd.server import server
from hyperion_node.cmd.appinfo import info, license
from hyperion_node.assets.license_text import text

# WICHTIG: Importiere deinen Service hier (Pfad ggf. anpassen)
from hyperion_node.services.server import HyperionServerService
from urllib.parse import urlparse
# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


@click.group(epilog="Copyright (C) 2026 Dein Name. Licensed under GPLv3.")
def cli():
    pass


async def run_worker():
    """Verbindet sich mit dem ersten Server und hält die Verbindung."""
    service = HyperionServerService()
    servers = service.get_all_servers()

    if not servers:
        logging.error("Keine Server in der Konfiguration gefunden.")
        return

    # Nur den ersten Server nehmen
    target_server = servers[0]
    url = urlparse(target_server.url)
    # Annahme: Dein Server-Objekt hat .ip und .port
    if url.scheme == "https":
        scheme = "wss"
    elif url.scheme == "http":
        scheme = "ws"
    uri = f"{scheme}://{url.hostname}:{url.port}/dmx?token={target_server.token}"

    logging.info(f"Worker gestartet. Ziel: {target_server.name} ({uri})")

    while True:
        try:
            logging.info(f"Versuche Verbindung zu {uri} ...")

            async with websockets.connect(uri) as ws:
                logging.info("✅ Verbunden! Warte auf Events...")

                # Endlosschleife, solange die Verbindung steht
                async for msg in ws:
                    # Hier später Nachrichten verarbeiten
                    print(msg)
            logging.warning("Verbindung vom Server geschlossen.")

        except (OSError, websockets.exceptions.ConnectionClosedError):
            logging.error("❌ Verbindung fehlgeschlagen oder unterbrochen.")
        except Exception as e:
            logging.error(f"Unerwarteter Fehler: {e}")

        logging.info("Warte 10 Sekunden vor Reconnect...")
        await asyncio.sleep(10)



@click.command(hidden=True)
def start_watchdog():
    """Der versteckte Prozess, der von Systemd oder manuell gestartet wird."""
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logging.info("Worker beendet.")


@click.command()
def enable():
    """Aktiviert den Hintergrunddienst (Linux: Systemd / Windows: Anleitung)."""
    current_os = platform.system()

    if current_os == "Linux":
        setup_systemd_service()
    elif current_os == "Windows":
        click.secho(
            "⚠ Windows erkannt: Systemd wird übersprungen.", fg='yellow')
        click.echo(
            "Zum Testen der Verbindung führe bitte diesen Befehl manuell aus:")
        # Baut den Befehl zusammen, um start-watchdog aufzurufen
        cmd_str = f"{sys.executable} {sys.argv[0]} start-watchdog"
        click.secho(f"\n    {cmd_str}\n", fg='green', bold=True)
        click.echo("Lass das Fenster offen, um die Verbindung zu simulieren.")
    else:
        click.echo(f"Betriebssystem {current_os} wird nicht unterstützt.")


def setup_systemd_service():
    """Linux-Helper: Erstellt die .service Datei."""
    SERVICE_NAME = "hyperion-node.service"
    SERVICE_PATH = f"/etc/systemd/system/{SERVICE_NAME}"

    python_path = sys.executable
    script_path = os.path.abspath(sys.argv[0])

    # Versuche User zu finden (falls sudo verwendet wird)
    user = os.environ.get('SUDO_USER', os.getlogin())

    service_content = f"""[Unit]
Description=Hyperion Node Connection Service
After=network.target

[Service]
Type=simple
User={user}
ExecStart={python_path} {script_path} start-watchdog
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    try:
        with open(SERVICE_PATH, "w") as f:
            f.write(service_content)
        click.secho(f"✔ Service-Datei erstellt: {SERVICE_PATH}", fg='green')

        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)
        subprocess.run(["systemctl", "start", SERVICE_NAME], check=True)

        click.secho("✔ Service erfolgreich gestartet!", fg='green', bold=True)
    except PermissionError:
        click.secho("Fehler: Bitte mit 'sudo' ausführen!", fg='red', bold=True)
    except Exception as e:
        click.secho(f"Fehler: {e}", fg='red')

# ------------------------------------------------------------------
# 3. REGISTRIERUNG
# ------------------------------------------------------------------


# Deine bestehenden Commands
cli.add_command(info)
cli.add_command(license)
cli.add_command(server)


cli.add_command(start_watchdog)
cli.add_command(enable)
