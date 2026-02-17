"""Application configuration and settings management."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class Settings:
    """Application settings manager."""

    def __init__(self, config_file: str = None):
        """Initialize settings.

        Args:
            config_file: Path to custom config file. If None, uses defaults.json
        """
        self._config = {}
        self._load_defaults()

        if config_file and os.path.exists(config_file):
            self._load_config(config_file)

    def _load_defaults(self):
        """Load default configuration."""
        defaults_path = Path(__file__).parent / "defaults.json"
        with open(defaults_path, 'r') as f:
            self._config = json.load(f)

    def _load_config(self, config_file: str):
        """Load custom configuration file.

        Args:
            config_file: Path to config file
        """
        with open(config_file, 'r') as f:
            custom_config = json.load(f)
            self._config.update(custom_config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'window.width')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, config_file: str):
        """Save current configuration to file.

        Args:
            config_file: Path to save config file
        """
        with open(config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    @property
    def pki_dir(self) -> str:
        """Get PKI directory path."""
        return self.get('pki_dir', '/home/pi/easy-rsa-pki')

    @property
    def easyrsa_bin(self) -> str:
        """Get easy-rsa binary path."""
        return self.get('easyrsa_bin', '/usr/share/easy-rsa/easyrsa')

    @property
    def usb_mount_points(self) -> list:
        """Get USB mount points to monitor."""
        return self.get('usb_mount_points', ['/media/pi', '/mnt/usb'])

    @property
    def template_dir(self) -> str:
        """Get template directory path."""
        return self.get('template_dir', 'templates/vars')

    @property
    def window_width(self) -> int:
        """Get window width."""
        return self.get('window.width', 480)

    @property
    def window_height(self) -> int:
        """Get window height."""
        return self.get('window.height', 320)

    @property
    def fullscreen(self) -> bool:
        """Get fullscreen mode setting."""
        return self.get('window.fullscreen', True)

    @property
    def content_width(self) -> int:
        """Get content area width."""
        return self.get('layout.content_width', 360)

    @property
    def button_width(self) -> int:
        """Get button area width."""
        return self.get('layout.button_width', 120)

    @property
    def button_height(self) -> int:
        """Get button height."""
        return self.get('layout.button_height', 40)

    @property
    def button_spacing(self) -> int:
        """Get button spacing."""
        return self.get('layout.button_spacing', 10)


# Global settings instance
settings = Settings()
