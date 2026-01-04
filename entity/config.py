# config.py
from typing import Any, Dict


class Config:
    """
    配置管理类，用于存储和管理应用程序的配置信息
    """
    _config: Dict[str, Any] = {
        "app_name": "default_app",
        "version": "v1",
    }

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项值
        """
        cls._config[key] = value

    @classmethod
    def get(cls, key: str, default=None) -> Any:
        """
        获取配置项值
        
        Args:
            key: 配置项键名
            default: 默认值，当键不存在时返回
            
        Returns:
            配置项的值，如果键不存在则返回默认值
        """
        return cls._config.get(key, default)

    @classmethod
    def set_app_name(cls, name: str) -> None:
        """
        设置应用名称
        
        Args:
            name: 应用名称
        """
        cls._config["app_name"] = name

    @classmethod
    def get_app_name(cls) -> str:
        """
        获取应用名称
        
        Returns:
            当前应用名称
        """
        return cls._config["app_name"]

    @classmethod
    def show(cls) -> None:
        """
        显示当前所有配置项
        """
        print(f"Current Config: {cls._config}")
