from time import perf_counter
from collections.abc import Iterator
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def track_duration(operation: str) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        logger.info("operation=%s duration_ms=%.2f", operation, (perf_counter() - start) * 1000)
