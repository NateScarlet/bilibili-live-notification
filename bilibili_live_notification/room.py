# -*- coding=UTF-8 -*-
"""live room operations.  """

import asyncio
import logging
import time
from typing import Dict, Tuple

from bilibili_api import live

from . import config

LOGGER = logging.getLogger(__name__)


def get(rid: str) -> dict:
    """Get room data.

    Args:
        rid (str): room id

    Returns:
        dict: normalized data
    """
    name = config.get_room_name(rid)
    info = live.get_room_info(rid)
    url = f'https://live.bilibili.com/{rid}'
    ret = dict(
        name=name,
        title=info["room_info"]["title"],
        url=url,
        data=info,
    )
    LOGGER.info("room data: %s: %s", rid, ret)
    return ret


_CACHE: Dict[str, Tuple[float, dict]] = dict()
_CACHE_MU = asyncio.locks.Lock()


async def get_with_cache(rid: str, *, ttl: float = 3600) -> dict:
    """Get room data with a ttl cache

    Args:
        rid (str): room id
        ttl (float, optional): cache time to live in seconds. Defaults to 3600.

    Returns:
        dict: room data.
    """
    rid = str(rid)
    async with _CACHE_MU:
        if (
            rid not in _CACHE or
            _CACHE[rid][0] < time.time() - ttl
        ):
            _CACHE[rid] = [time.time(), get(rid)]
    return _CACHE[rid][1]
