import logging
from pathlib import Path
from uuid import uuid7
from datetime import datetime
import toml  # pip install toml


class Config:
    def __init__(self):
        self.cnf_path = Path.home() / ".hyperion_node"
        self.cnf_file = self.cnf_path / "config.toml"

        # Interner Cache für die Config-Daten
        self._data = {}

        self.setup()
        self.load()

    def setup(self):
        """Erstellt Ordner und Standard-Config, falls nicht vorhanden."""
        if not self.cnf_path.exists():
            self.cnf_path.mkdir(parents=True, exist_ok=True)

        if not self.cnf_file.exists():
            # Standard-Werte setzen
            default_config = {
                "node": {
                    "id": str(uuid7()),
                    "created_at": datetime.now().isoformat(),
                    "default_port": 2468,
                    "debug": False
                },
                "servers": {}  # Leerer Container für Server
            }
            self.save(default_config)

    def load(self):
        """Lädt die TOML Datei in den Speicher."""
        try:
            with open(self.cnf_file, "r") as f:
                self._data = toml.load(f)
        except Exception as e:
            logging.error(f"Fehler beim Laden der Config: {e}")
            # Fallback, falls Datei korrupt ist
            self._data = {"node": {}, "servers": {}}

    def save(self, data=None):
        """Speichert Daten in die TOML Datei."""
        if data is None:
            data = self._data

        with open(self.cnf_file, "w") as f:
            toml.dump(data, f)

        # Update internal cache
        self._data = data

    # --- Generische Getter/Setter ---

    def get_setting(self, key, default=None):
        """Holt Einstellungen aus der [node] Sektion."""
        return self._data.get("node", {}).get(key, default)

    def set_setting(self, key, value):
        """Setzt Einstellungen in der [node] Sektion."""
        if "node" not in self._data:
            self._data["node"] = {}

        self._data["node"][key] = value
        self.save()

    # --- Server Management ---

    def add_server(self, name: str, server_data: dict):
        """Fügt einen Server hinzu oder aktualisiert ihn."""
        if "servers" not in self._data:
            self._data["servers"] = {}

        # Optional: Check ob Name schon vergeben
        if name in self._data["servers"]:
            # Logging oder Error, je nach Wunsch
            pass

        self._data["servers"][name] = server_data
        self.save()

    def get_server(self, name: str):
        return self._data.get("servers", {}).get(name)

    def get_all_servers(self):
        return self._data.get("servers", {})

    def remove_server(self, name: str):
        if "servers" in self._data and name in self._data["servers"]:
            del self._data["servers"][name]
            self.save()
            return True
        return False


cnf = Config()
