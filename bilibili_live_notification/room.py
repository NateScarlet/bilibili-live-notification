# -*- coding=UTF-8 -*-
"""live room operations.  """

import logging

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
