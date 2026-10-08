import re
from typing import Union
from bs4 import BeautifulSoup


def format_bytes(size: Union[int, float]) -> str:
    """Formats bytes into human-readable representation."""
    if not size:
        return "0 B"
    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"


def format_time(seconds: Union[int, float]) -> str:
    """Formats seconds into readable d/h/m/s representation."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def progress_bar(current: int, total: int, length: int = 12) -> str:
    """
    Renders an ASCII/Unicode progress bar with percentage and size details.
    Example: [██████░░░░░░] 50% (10 MB / 20 MB)
    """
    if total <= 0:
        return f"`[⏳ Loading...]` ({format_bytes(current)})"

    percent = min(1.0, current / total)
    filled_len = int(round(length * percent))
    bar = "█" * filled_len + "░" * (length - filled_len)
    pct_text = f"{int(percent * 100)}%"
    sizes = f"{format_bytes(current)} / {format_bytes(total)}"
    return f"`[{bar}]` **{pct_text}** ({sizes})"


def clean_html_to_markdown(html_content: str, max_chars: int = 3500) -> str:
    """
    Strips scripts, styles, navigations and extracts readable text formatted as clean markdown.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
        tag.decompose()

    # Extract text
    text = soup.get_text(separator="\n", strip=True)

    # Clean multiple blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n\n".join(lines)

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n... *(Content truncated)*"

    return cleaned


def escape_markdown(text: str) -> str:
    """Escapes Telegram markdown characters."""
    chars = ["_", "*", "`", "[", "]"]
    for c in chars:
        text = text.replace(c, f"\\{c}")
    return text
