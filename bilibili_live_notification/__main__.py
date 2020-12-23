import asyncio
import logging
import os
from datetime import datetime

from bilibili_api import live

from . import config, emailtools


def _get_room_name(rid):
    return os.getenv(f'BILIBILI_ROOM_NAME_{rid}') or rid


async def _debug(event):
    logging.debug(event)


async def _handle_live(event):
    logging.info(event)
    emailtools.send(
        config.EMAIL_TO,
        f'[开播]{_get_room_name(event["room_display_id"])}',
        f'{datetime.now()} https://live.bilibili.com/{event["room_display_id"]} ',
    )


def iterate_rooms():
    for i in config.BILIBILI_ROOM_ID:
        room = live.LiveDanmaku(i)
        room.on("LIVE")(_handle_live)
        yield room


# https://github.com/Passkou/bilibili_api/pull/91
def connect_all_LiveDanmaku(*livedanmaku_classes):
    """
    同时连接多个直播间
    :param livedanmaku_classes: LiveDanmaku类动态参数
    :return:
    """
    tasks = []
    for room in livedanmaku_classes:
        task = room.connect(True)
        tasks.append(task)

    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)
    if config.TEST_EMAIL_TO:
        logging.info('发送测试邮件')
        emailtools.send(
            config.TEST_EMAIL_TO,
            '[启动]哔哩哔哩开播提醒',
            f'{datetime.now()} 服务启动测试邮件',
        )
    connect_all_LiveDanmaku(*iterate_rooms())
