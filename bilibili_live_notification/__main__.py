"""Send email notification when bilibili live start. """
import asyncio
import logging
from datetime import datetime, timedelta

from bilibili_api import live

from . import config, emailtools


async def _debug(event):
    logging.debug(event)


def _format_time(v: datetime) -> str:
    return v.strftime("%Y-%m-%d %H:%M:%S")


LAST_EMAIL_SEND_TIME = {}


async def _handle_live(event):
    logging.info(event)
    rid = event["room_display_id"]

    now = datetime.now()
    if (rid in LAST_EMAIL_SEND_TIME and
            LAST_EMAIL_SEND_TIME[rid] > now - timedelta(seconds=config.BILIBILI_EMAIL_THROTTLE)):
        logging.info("email throttled: %s", rid)
        return

    emailtools.send(
        config.get_room_email_to(rid),
        f'[开播]{config.get_room_name(rid)}',
        f'{_format_time(now)} https://live.bilibili.com/{rid} ',
    )
    LAST_EMAIL_SEND_TIME[rid] = now


def iterate_rooms():
    for i in config.discover_bilibili_room_id():
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
            f'{_format_time(datetime.now())} 服务启动测试邮件',
        )
    connect_all_LiveDanmaku(*iterate_rooms())
