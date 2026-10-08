import time
from collections import defaultdict
from threading import Lock
from typing import Tuple


class InMemoryRateLimiter:
    """Thread-safe sliding-window in-memory rate limiter."""
    def __init__(self):
        self._records = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, max_attempts: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under the rate limit.
        Returns: (is_allowed: bool, remaining_attempts: int)
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            # Purge timestamps outside the window
            timestamps = [ts for ts in self._records[key] if ts > cutoff]
            if len(timestamps) >= max_attempts:
                self._records[key] = timestamps
                return False, 0

            timestamps.append(now)
            self._records[key] = timestamps
            remaining = max(0, max_attempts - len(timestamps))
            return True, remaining

    def reset(self, key: str):
        with self._lock:
            if key in self._records:
                del self._records[key]

    def clear_all(self):
        with self._lock:
            self._records.clear()


limiter = InMemoryRateLimiter()
