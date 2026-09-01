#!/usr/bin/env python3
"""
ENI Plugin Manager - Hot-reloadable modular tools
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger("PluginManager")

class PluginManager:
    def __init__(self, plugin_dir: Path = None):
        self.plugin_dir = plugin_dir or Path.home() / '.eni' / 'plugins'
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Any] = {}
        self.commands: Dict[str, Callable] = {}

    def discover(self):
        """Scan plugin directory and load all valid plugins"""
        for path in self.plugin_dir.glob("*/plugin.py"):
            name = path.parent.name
            try:
                self.load_plugin(name, path)
            except Exception as e:
                logger.error(f"Failed to load plugin {name}: {e}")

    def load_plugin(self, name: str, path: Path):
        """Load a single plugin module"""
        spec = importlib.util.spec_from_file_location(f"eni_plugin_{name}", path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "PLUGIN_META"):
            raise ValueError(f"Plugin {name} missing PLUGIN_META")

        meta = module.PLUGIN_META
        self.plugins[name] = {
            "module": module,
            "meta": meta,
            "path": path
        }

        # Register commands if present
        if hasattr(module, "register_commands"):
            cmds = module.register_commands()
            for cmd_name, func in cmds.items():
                self.commands[cmd_name] = func
                logger.info(f"Registered command: {cmd_name} from {name}")

        logger.info(f"Loaded plugin: {name} v{meta.get('version', '?')}")

    def get_plugin(self, name: str) -> Optional[Dict]:
        return self.plugins.get(name)

    def list_plugins(self):
        return [
            {"name": n, **p["meta"]} for n, p in self.plugins.items()
        ]

    def run_command(self, cmd: str, *args, **kwargs):
        if cmd not in self.commands:
            raise KeyError(f"Unknown plugin command: {cmd}")
        return self.commands[cmd](*args, **kwargs)

# Singleton
_pm = None
def get_plugin_manager():
    global _pm
    if _pm is None:
        _pm = PluginManager()
        _pm.discover()
    return _pm
