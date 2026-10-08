import importlib
import inspect
import sys
from pathlib import Path
from typing import List

from config import config
from .logger import log
from .decorators import COMMAND_REGISTRY


LOADED_HANDLERS = []


def load_plugins(client) -> int:
    """
    Dynamically scans and imports all modules in the plugins/ folder.
    Registers all decorated functions to the Telethon client.
    """
    plugin_files = list(config.PLUGIN_DIR.glob("*.py"))
    loaded_count = 0

    for file_path in plugin_files:
        if file_path.name.startswith("__"):
            continue

        module_name = f"plugins.{file_path.stem}"
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            client.plugins[file_path.stem] = module
            
            # Inspect all callable functions in the module
            registered_in_module = 0
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, "event_filter"):
                    client.add_event_handler(attr, attr.event_filter)
                    LOADED_HANDLERS.append(attr)
                    registered_in_module += 1

            log.info(f"Loaded plugin: {file_path.stem} ({registered_in_module} commands)")
            loaded_count += 1
        except Exception as e:
            log.error(f"Failed to load plugin '{file_path.stem}': {e}", exc_info=True)

    client.commands = COMMAND_REGISTRY
    return loaded_count


def reload_plugins(client) -> int:
    """
    Removes currently active event handlers and re-imports all plugins cleanly.
    """
    global LOADED_HANDLERS
    log.info("Hot-reloading all plugins...")

    for handler in LOADED_HANDLERS:
        try:
            client.remove_event_handler(handler)
        except Exception:
            pass

    LOADED_HANDLERS.clear()
    COMMAND_REGISTRY.clear()
    client.plugins.clear()
    client.commands.clear()

    return load_plugins(client)
