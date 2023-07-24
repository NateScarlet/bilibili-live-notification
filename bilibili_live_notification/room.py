# -*- coding=UTF-8 -*-
"""live room operations.  """

import asyncio
import aiohttp.client_exceptions
import contextvars
import logging
import time
from collections import defaultdict
from typing import Dict, Tuple

from bilibili_api import live

from . import config, rate_limit

LOGGER = logging.getLogger(__name__)


async def _fetch(rid: str) -> dict:
    """Get room data.

    Args:
        rid (str): room id

    Returns:
        dict: normalized data
    """
    LOGGER.info("will fetch: %s", rid)
    name = config.get_room_name(rid)
    info = await live.LiveRoom(rid).get_room_info()  # type: ignore
    assert info, "info is None"
    url = f"https://live.bilibili.com/{rid}"
    ret = dict(
        name=name,
        title=info["room_info"]["title"],
        url=url,
        data=info,
        popularity=info["room_info"]["online"],
    )
    LOGGER.debug("did fetch: %s: %s", rid, ret)
    return ret


_CACHE: Dict[str, Tuple[float, dict]] = dict()
ROOM_POPUPARITY = defaultdict(lambda: 0)


async def get(rid: str, *, ttl: float = 3600) -> dict:
    """Get room data with a ttl cache

    Args:
        rid (str): room id
        ttl (float, optional): cache time to live in seconds. Defaults to 3600.

    Returns:
        dict: room data.
    """
    await asyncio.sleep(0)
    rid = str(rid)
    try:
        if rid not in _CACHE or _CACHE[rid][0] < time.time() - ttl:
            await rate_limit.BILIBILI_API.get().wait()
            entry = (time.time(), await _fetch(rid))
            _CACHE[rid] = entry
            ROOM_POPUPARITY[rid] = entry[1]["popularity"]
    except aiohttp.client_exceptions.ClientOSError:
        LOGGER.warning("possible rate limit reached during fetch: %s, will retry", rid)
        await asyncio.sleep(0)
        return await get(rid, ttl=ttl)

    _, ret = _CACHE[rid]
    ret["popularity"] = ROOM_POPUPARITY[rid]
    return ret
