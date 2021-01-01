"""Send email notification when bilibili live start. """
import logging
from datetime import datetime, timedelta

from bilibili_api import live

from . import config, emailtools


def _format_time(v: datetime) -> str:
    return v.strftime("%H:%M:%S %Y-%m-%d")


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
        f'[开播]{config.get_room_name(rid)} - {_format_time(now)}',
        f'https://live.bilibili.com/{rid} ',
    )
    LAST_EMAIL_SEND_TIME[rid] = now


def iterate_rooms():
    for i in config.discover_bilibili_room_id():
        room = live.LiveDanmaku(i)
        room.on("LIVE")(_handle_live)
        yield room


if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)
    if config.TEST_EMAIL_TO:
        logging.info('发送测试邮件')
        emailtools.send(
            config.TEST_EMAIL_TO,
            f'[启动] - {_format_time(datetime.now())}',
            '服务启动测试邮件',
        )
    live.connect_all_LiveDanmaku(*iterate_rooms())
