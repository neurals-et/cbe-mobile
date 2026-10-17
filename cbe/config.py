"""
Configuration & Settings Manager for CBE Mobile Client
"""

import json
import os
from typing import Dict, Any

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.cbe_config.json")
DEFAULT_API_BASE = "https://mb.cbe.com.et/api"
DEFAULT_FOREX_URL = "https://combanketh.et/cbeapi/daily-exchange-rates/"


class CBEConfig:
    """Configuration and credentials manager for CBE Mobile."""

    def __init__(self, filepath: str = DEFAULT_CONFIG_PATH):
        self.filepath = filepath
        self.defaults = {
            "api_base": DEFAULT_API_BASE,
            "forex_url": DEFAULT_FOREX_URL,
            "phone_number": "+251911000000",
            "account_number": "1000123456789",
            "device_id": "cbe_dev_e018a3",
            "device_model": "Samsung SM-A075F",
            "access_token": "",
            "handshake_id": "",
            "mock_mode": True
        }
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cfg = self.defaults.copy()
                    cfg.update(saved)
                    return cfg
            except Exception:
                pass
        return self.defaults.copy()

    def save(self) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default if default is not None else self.defaults.get(key))

    def set(self, key: str, value: Any):
        self.data[key] = value

    def reset(self):
        self.data = self.defaults.copy()
        self.save()
