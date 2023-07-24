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
    await rate_limit.BILIBILI_API.get().wait()
    start_time = time.time()
    LOGGER.info("will fetch: id=%s", rid)
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
    LOGGER.info("did fetch: id=%s elapsed=%fs", rid, time.time() - start_time)
    return ret


_CACHE: Dict[str, Tuple[float, dict]] = dict()
ROOM_POPUPARITY = defaultdict(lambda: 0)
_SINGLE_FLIGHT = defaultdict(lambda: asyncio.locks.Lock())


async def get(rid: str, *, max_age_secs: float = 3600) -> dict:
    """Get room data with a ttl cache

    Args:
        rid (str): room id
        ttl (float, optional): cache time to live in seconds. Defaults to 3600.

    Returns:
        dict: room data.
    """

    rid = str(rid)
    if rid not in _CACHE or time.time() - _CACHE[rid][0] > max_age_secs:
        in_flight = _SINGLE_FLIGHT[rid].locked()
        try:
            async with _SINGLE_FLIGHT[rid]:
                if not in_flight:
                    entry = (time.time(), await _fetch(rid))
                    _CACHE[rid] = entry
                    ROOM_POPUPARITY[rid] = entry[1]["popularity"]
        except aiohttp.client_exceptions.ClientOSError:
            LOGGER.warning(
                "possible rate limit reached during fetch: %s, will retry", rid
            )
            await asyncio.sleep(0)
            return await get(rid, max_age_secs=max_age_secs)

    _, ret = _CACHE[rid]
    ret["popularity"] = ROOM_POPUPARITY[rid]
    return ret
