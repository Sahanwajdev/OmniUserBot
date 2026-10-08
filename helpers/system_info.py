import os
import platform
import psutil
import telethon
from typing import Dict, Any

from .formatting import format_bytes


def get_system_summary() -> Dict[str, Any]:
    """Retrieves full host system performance metrics."""
    # Memory
    mem = psutil.virtual_memory()
    total_mem = format_bytes(mem.total)
    used_mem = format_bytes(mem.used)
    mem_percent = mem.percent

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_phys = psutil.cpu_count(logical=False) or cpu_cores

    # Disk
    disk = psutil.disk_usage(os.path.abspath(os.sep))
    disk_total = format_bytes(disk.total)
    disk_used = format_bytes(disk.used)
    disk_percent = disk.percent

    # Platform
    os_name = platform.system()
    os_release = platform.release()
    os_arch = platform.machine()
    python_ver = platform.python_version()

    return {
        "os": f"{os_name} {os_release} ({os_arch})",
        "python": python_ver,
        "telethon": telethon.__version__,
        "cpu_usage": f"{cpu_percent}%",
        "cpu_cores": f"{cpu_phys}C / {cpu_cores}T",
        "ram_usage": f"{used_mem} / {total_mem} ({mem_percent}%)",
        "ram_percent": mem_percent,
        "disk_usage": f"{disk_used} / {disk_total} ({disk_percent}%)",
        "disk_percent": disk_percent,
    }
