import logging
import sys
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


class OmniFormatter(logging.Formatter):
    """Custom color formatter for OmniUserBot logs."""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN if HAS_COLOR else "",
        logging.INFO: Fore.GREEN if HAS_COLOR else "",
        logging.WARNING: Fore.YELLOW if HAS_COLOR else "",
        logging.ERROR: Fore.RED if HAS_COLOR else "",
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT if HAS_COLOR else "",
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        reset_color = Style.RESET_ALL if HAS_COLOR else ""
        dim_color = Fore.LIGHTBLACK_EX if HAS_COLOR else ""

        time_str = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"{dim_color}[{time_str}]{reset_color} {level_color}[{record.levelname:<7}]{reset_color}"
        message = record.getMessage()

        if record.exc_info:
            text = super().format(record)
            return f"{prefix} {text}"
        return f"{prefix} {message}"


def setup_logger(name: str = "OmniUserBot", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(OmniFormatter())
        logger.addHandler(handler)

    # Mute noisy telethon info/debug logs
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logger


log = setup_logger()
