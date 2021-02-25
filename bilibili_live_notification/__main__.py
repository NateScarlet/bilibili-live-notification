"""Send email notification when bilibili live start. """
import asyncio
import logging
from datetime import datetime, timedelta

from bilibili_api import live

from . import config, emailtools, webhook


def _format_time(v: datetime) -> str:
    return v.strftime("%H:%M:%S %Y-%m-%d")


LOGGER = logging.getLogger(__name__)
LAST_EMAIL_SEND_TIME = {}


async def _handle_live(event):
    LOGGER.info(event)
    rid = event["room_display_id"]

    now = datetime.now()
    if (rid in LAST_EMAIL_SEND_TIME and
            LAST_EMAIL_SEND_TIME[rid] > now - timedelta(seconds=config.BILIBILI_EMAIL_THROTTLE)):
        LOGGER.info("email throttled: %s", rid)
        return

    room_data = live.get_room_info(rid)
    name = config.get_room_name(rid)
    url = f'https://live.bilibili.com/{rid}'
    await webhook.triggerMany(
        (config.get_csv(f"BILIBILI_ROOM_LIVE_WEBHOOK_{rid}") or
         config.get_csv(f"BILIBILI_LIVE_WEBHOOK")),
        dict(
            event=event,
            room=dict(
                name=name,
                title=room_data["room_info"]["title"],
                url=url,
                data=room_data,
            ),
        )
    )
    # TODO: support template for email subject and body
    emailtools.send(
        config.get_room_email_to(rid),
        f'[开播]{config.get_room_name(rid)} - {_format_time(now)}',
        f'{url} ',
    )
    LAST_EMAIL_SEND_TIME[rid] = now


def iterate_rooms():
    for i in config.discover_bilibili_room_id():
        room = live.LiveDanmaku(i)
        room.on("LIVE")(_handle_live)
        yield room


if __name__ == '__main__':
    LOGGER.setLevel(logging.INFO)
    webhook.LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    LOGGER.addHandler(handler)
    webhook.LOGGER.addHandler(handler)
    asyncio.get_event_loop().run_until_complete(
        webhook.triggerMany(config.get_csv("SERVER_START_WEBHOOK")),
    )
    if config.TEST_EMAIL_TO:
        LOGGER.info('发送测试邮件')
        emailtools.send(
            config.TEST_EMAIL_TO,
            f'[启动] - {_format_time(datetime.now())}',
            '服务启动测试邮件',
        )
    live.connect_all_LiveDanmaku(*iterate_rooms())
    LOGGER.info('未配置要监控的直播间，请查看 README.md')
