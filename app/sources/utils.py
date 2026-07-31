import re
from datetime import UTC, datetime
from html import unescape


def clean_html(value: str) -> str:
    """Convert job-board HTML into safe plain text for search and Telegram."""
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def parse_datetime(value: str | int | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, int):
        return datetime.fromtimestamp(value, tz=UTC)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
