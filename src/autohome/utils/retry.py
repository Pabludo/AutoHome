"""Retry utilities with exponential backoff."""

import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def retry_async(max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
    """Decorator for async functions with exponential backoff retry."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = base_delay

            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Attempt %d/%d for %s failed: %s. Retrying in %.1fs",
                            attempt,
                            max_retries,
                            func.__name__,
                            e,
                            delay,
                        )
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            "All %d attempts for %s failed",
                            max_retries,
                            func.__name__,
                        )

            raise last_exception

        return wrapper

    return decorator
