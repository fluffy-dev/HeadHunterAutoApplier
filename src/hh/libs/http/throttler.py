import asyncio
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class RateLimitConfig:
    limit: int = 5  # Requests
    window: int = 1  # Second


@dataclass
class HostBucket:
    timestamps: deque = field(default_factory=deque)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class AsyncThrottler:
    """
    Manages rate limiting per host to avoid 429 errors using asyncio.Lock.
    """

    def __init__(self, config: RateLimitConfig | None = None):
        self.config = config or RateLimitConfig()
        self._buckets: dict[str, HostBucket] = {}

    def _get_bucket(self, key: str) -> HostBucket:
        if key not in self._buckets:
            self._buckets[key] = HostBucket()
        return self._buckets[key]

    async def acquire(self, key: str):
        bucket = self._get_bucket(key)

        async with bucket.lock:
            now = time.monotonic()

            # Remove timestamps older than the window
            while bucket.timestamps and now - bucket.timestamps[0] > self.config.window:
                bucket.timestamps.popleft()

            if len(bucket.timestamps) >= self.config.limit:
                wait_time = self.config.window - (now - bucket.timestamps[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            bucket.timestamps.append(time.monotonic())