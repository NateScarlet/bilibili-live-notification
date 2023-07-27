# -*- coding=UTF-8 -*-
"""Execute webhooks.  """

import asyncio
import logging
from typing import Iterable, Optional

import aiohttp
from aiohttp.client_exceptions import ClientError

from . import config

_LOGGER = logging.getLogger(__name__)

_RETRY_DELAY = {
    5: 1,
    4: 10,
    3: 60,
    2: 300,
    1: 600,
}


async def trigger(
    name: str, data: Optional[dict] = None, *, max_retry: int = 3
) -> None:
    try:
        if config.get(f"WEBHOOK_SKIP_{name}", data).lower() == "true":
            _LOGGER.info("skip: %s", name)
            return
        _LOGGER.info("will trigger: %s", name)
        url = config.get(f"WEBHOOK_URL_{name}", data)
        method = config.get(f"WEBHOOK_METHOD_{name}", data)
        headers = {
            k.replace("_", "-").lower(): v
            for k, v in config.get_items(f"WEBHOOK_HEADER_{name}_", data)
        }
        body = config.get(f"WEBHOOK_BODY_{name}", data)
        async with aiohttp.request(method, url, headers=headers, data=body) as resp:
            _LOGGER.info(
                "did trigger: %s: %s: %s", name, resp.status, await resp.read()
            )
    except Exception:
        _LOGGER.exception("failed: %s", name)
        if max_retry > 0:
            delay = _RETRY_DELAY.get(max_retry, 1)
            _LOGGER.info("will retry after %ds: %s", delay, name)
            await asyncio.sleep(delay)
            await trigger(name, data, max_retry=max_retry - 1)


async def trigger_many(names: Iterable[str], data: Optional[dict] = None) -> None:
    await asyncio.gather(*(trigger(i, data) for i in names))
