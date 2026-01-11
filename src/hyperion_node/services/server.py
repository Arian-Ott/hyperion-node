from urllib.parse import urlparse
from hyperion_node.core.config import cnf
import requests


class HyperionServerService:
    DEFAULT_PORT = 2468

    def __init__(self):
        self.cnf = cnf

    def resolve_connection_details(
        self, address: str = None, host_override: str = None, port_override: int = None
    ):
        """
        Analysiert die Eingaben und gibt saubere (host, port) zurück.
        Wirft ValueError bei ungültigen Eingaben.
        """
        final_host = None
        final_port = None

        # --- 1. Address Parsing (URLLIB Logic) ---
        if address:
            # Trick: "//" davor, damit urlparse auch ohne Protokoll (http) parst
            parse_target = address
            if "://" not in parse_target and not parse_target.startswith("//"):
                parse_target = "//" + parse_target

            try:
                parsed = urlparse(parse_target)

                if parsed.hostname:
                    final_host = parsed.hostname

                if parsed.port:
                    final_port = parsed.port

            except ValueError:
                raise ValueError(f"Die Adresse '{address}' hat ein ungültiges Format.")

        # --- 2. Overrides (Flags gewinnen) ---
        if host_override:
            final_host = host_override
        if port_override:
            final_port = port_override

        # --- 3. Validierung & Defaults ---
        if not final_host:
            raise ValueError(
                "Ein Hostname ist erforderlich (entweder in der Adresse oder via -H)."
            )

        if not final_port:
            final_port = self.DEFAULT_PORT

        if not (1 <= final_port <= 65535):
            raise ValueError(f"Port {final_port} ist ungültig (muss 1-65535 sein).")

        return final_host, final_port

    def connect_server(self, host: str, port: int):
        """
        Führt die eigentliche Verbindung und Speicherung durch.
        """
        # Hier kommt später dein Ping / Connection Test hin
        print(f"DEBUG: Service verbindet zu {host}:{port}...")

        # Speichern in der Config
        self.cnf.set_setting("hyperion-server", "host", host)
        self.cnf.set_setting("hyperion-server", "port", port)

        return True
