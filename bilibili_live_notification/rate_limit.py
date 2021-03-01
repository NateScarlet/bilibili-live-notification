# -*- coding=UTF-8 -*-
"""Limit operation rate.  """


import asyncio
import contextvars
import time


class RateLimiter():
    """Rate limit of size {size}, and increase by {rate} per second.
    """
    def __init__(self, size: float, rate: float):
        self.size = size
        self.rate = rate
        self.allowance = 0
        self.last_check_time = time.time()
        self.mu = asyncio.locks.Lock()

    async def wait(self, n=1):
        """Wait n allowance.

        Args:
            n (int, optional): number. Defaults to 1.
        """
        async with self.mu:
            self._update_allowance()
            while self.allowance < n:
                await asyncio.sleep(0)
                self._update_allowance()
            self.allowance -= n

    def _update_allowance(self):
        now = time.time()
        self.allowance = min(
            self.allowance+(now - self.last_check_time) * self.rate,
            self.size,
        )
        self.last_check_time = now


BILIBILI_API = contextvars.ContextVar("RATE_LIMIT")
