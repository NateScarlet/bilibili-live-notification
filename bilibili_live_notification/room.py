# -*- coding=UTF-8 -*-
"""live room operations.  """

import asyncio
import contextvars
import logging
import time
from typing import Dict, Tuple

from bilibili_api import live

from . import config, rate_limit

LOGGER = logging.getLogger(__name__)

def get(rid: str) -> dict:
    """Get room data.

    Args:
        rid (str): room id

    Returns:
        dict: normalized data
    """
    LOGGER.info("fetch room data: %s", rid)
    name = config.get_room_name(rid)
    info = live.get_room_info(rid)
    url = f'https://live.bilibili.com/{rid}'
    ret = dict(
        name=name,
        title=info["room_info"]["title"],
        url=url,
        data=info,
    )
    LOGGER.debug("room data: %s: %s", rid, ret)
    return ret


_CACHE: Dict[str, Tuple[float, dict]] = dict()
CACHE_MU = contextvars.ContextVar("CACHE_MU")

async def get_with_cache(rid: str, *, ttl: float = 3600) -> dict:
    """Get room data with a ttl cache

    Args:
        rid (str): room id
        ttl (float, optional): cache time to live in seconds. Defaults to 3600.

    Returns:
        dict: room data.
    """
    await asyncio.sleep(0)
    rid = str(rid)
    async with CACHE_MU.get():
        if (
            rid not in _CACHE or
            _CACHE[rid][0] < time.time() - ttl
        ):
            await rate_limit.BILIBILI_API.get().wait()
            _CACHE[rid] = [time.time(), get(rid)]
    return _CACHE[rid][1]
