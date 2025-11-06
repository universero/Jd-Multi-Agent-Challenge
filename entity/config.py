# config.py
from typing import Any, Dict


class Config:
    _config: Dict[str, Any] = {
        "app_name": "default_app",
        "version": "v1",
    }

    @classmethod
    def set(cls, key: str, value: Any):
        cls._config[key] = value

    @classmethod
    def get(cls, key: str, default=None) -> Any:
        return cls._config.get(key, default)

    @classmethod
    def set_app_name(cls, name: str):
        cls._config["app_name"] = name

    @classmethod
    def get_app_name(cls) -> str:
        return cls._config["app_name"]

    @classmethod
    def show(cls):
        print(f"Current Config: {cls._config}")
