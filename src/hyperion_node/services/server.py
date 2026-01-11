from urllib.parse import urlparse
from hyperion_node.core.config import cnf
import requests
import click
from dataclasses import dataclass

@dataclass
class HyperionServerObj:
    name: str
    url:str
    token:str

class HyperionServerService:
    DEFAULT_PORT = 2468

    def __init__(self):
        self.cnf = cnf

    def connect_server(self, url: str, otp: str, name: str):
        """
        Führt die eigentliche Verbindung und Speicherung durch.
        """
        if url.endswith("/"):
            url = url[:-1]
        if self.cnf.get_server(name):
            raise click.UsageError("Server already exists")
        response = requests.post(url + "/api/dmx/otp-authenticate", json={"otp": otp, "name": name})
        response = response.json()

        self.cnf.add_server(name, {
            "url": url,
            "device_secret": response.get("device_secret"),
            "exp": response.get("exp")
            
        })

        return True

    def get_all_servers(self):
        """
        Liest das Dictionary aus der Config und wandelt es 
        in eine Liste von Objekten um.
        """
        raw_servers = cnf.get_all_servers()  # Das kommt aus deiner Config Klasse
        server_list = []

        # Wir iterieren durch das Dictionary
        for name, data in raw_servers.items():
            # Einfache Validierung: Sind IP und Port da?
            if "url" in data.keys():
                obj = HyperionServerObj(
                    name=name,
                    url=data["url"],
                    token=data["device_secret"]
                )
                server_list.append(obj)

        return server_list
