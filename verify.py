import sys
from pathlib import Path

# Configure utf-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add repo to sys.path
repo_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_dir))

import config
import core.logger
import core.decorators
import core.loader

print("Dynamically discovering and importing all plugins...")
plugin_files = list(config.PLUGIN_DIR.glob("*.py"))
for f in plugin_files:
    if not f.name.startswith("__"):
        import importlib
        importlib.import_module(f"plugins.{f.stem}")

print(f"\n✅ Total registered commands: {len(core.decorators.COMMAND_REGISTRY)}")
for cmd, meta in sorted(core.decorators.COMMAND_REGISTRY.items()):
    cat = meta.get("category", "General")
    desc = meta.get("description", "")
    print(f"  • {cmd:<12} [{cat:<10}] {desc}")

print("\n🚀 ALL MODULES AND COMMANDS VERIFIED CLEANLY WITH ZERO ERRORS!")
