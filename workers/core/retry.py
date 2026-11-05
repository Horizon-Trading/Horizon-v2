import time
import httpx
from postgrest.exceptions import APIError


def retry_persistence(operation):
    """Retry only idempotent persistence, never broker order submissions."""
    for attempt in range(3):
        try:
            return operation()
        except (httpx.TransportError, APIError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)
