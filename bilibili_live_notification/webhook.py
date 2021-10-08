# -*- coding=UTF-8 -*-
"""Execute webhooks.  """

import asyncio
import logging
from typing import Iterable, Optional

import aiohttp
from aiohttp.client_exceptions import ClientError

from . import config

LOGGER = logging.getLogger(__name__)


async def trigger(name: str, data: Optional[dict] = None) -> None:
    if config.get(f"WEBHOOK_SKIP_{name}", data).lower() == "true":
        LOGGER.info("webhook skip: %s", name)
        return
    LOGGER.info("webhook start: %s", name)
    url = config.get(f"WEBHOOK_URL_{name}", data)
    method = config.get(f"WEBHOOK_METHOD_{name}", data)
    headers = {
        k.replace("_", "-").lower(): v
        for k, v in config.get_items(f"WEBHOOK_HEADER_{name}_", data)
    }
    body = config.get(f"WEBHOOK_BODY_{name}", data)
    try:
        async with aiohttp.request(method, url, headers=headers, data=body) as resp:
            LOGGER.info(
                "webhook done: %s: %s: %s", name, resp.status, await resp.read()
            )
    except ClientError as ex:
        LOGGER.error("webhook failed: %s: %s", name, ex)


async def trigger_many(names: Iterable[str], data: Optional[dict] = None) -> None:
    await asyncio.gather(*(trigger(i, data) for i in names))
