"""Config from environment variables."""

import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from env_proxy import EnvProxy

load_dotenv()


class Configuration:
    """Configuration abstraction for OpenAI Helper."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else Path.home() / ".config" / ".openai_helper" / "config.json"
        self._config: dict[str, Any] = self._load()

    @property
    def config(self) -> dict[str, Any]:
        """Configuration dictionary"""
        self._config = self._load()
        return self._config

    def _load(self) -> dict[str, Any]:
        """Load config from file"""
        if not self.path.exists():
            return {}
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self) -> None:
        """Save config to file"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self._config, file, indent=4)

    def __getattr__(self, name: str) -> Any:
        return self._load().get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("config", "path", "_config"):
            return super().__setattr__(name, value)
        self._config[name] = value
        self._save()
        return None


__all__ = ["EnvProxy", "Configuration"]
