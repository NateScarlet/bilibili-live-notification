"""Send email notification when bilibili live start. """
import asyncio
import logging
from datetime import datetime, timedelta

from bilibili_api import live

from . import config, emailtools, webhook, room


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

    room_data = room.get(rid)

    await webhook.trigger_many(
        (config.get_csv(f"BILIBILI_ROOM_LIVE_WEBHOOK_{rid}") or
         config.get_csv("BILIBILI_LIVE_WEBHOOK")),
        {
            **dict(
                event=event,
                room=room_data,
            ),
            **dict(config.get_items(f"BILIBILI_ROOM_TEMPLATE_VAR_{rid}_")),
        },
    )
    # TODO: support template for email subject and body
    emailtools.send(
        config.get_room_email_to(rid),
        f'[开播]{room_data["name"]} - {_format_time(now)}',
        f'{room_data["url"]} ',
    )
    LAST_EMAIL_SEND_TIME[rid] = now


def _iterate_rooms():
    for i in config.discover_bilibili_room_id():
        room1 = live.LiveDanmaku(i)
        room1.on("LIVE")(_handle_live)
        yield room1


if __name__ == '__main__':
    all_logger = [LOGGER, webhook.LOGGER, room.LOGGER]
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    for logger in [LOGGER, webhook.LOGGER, room.LOGGER]:
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    asyncio.get_event_loop().run_until_complete(
        webhook.trigger_many(config.get_csv("SERVER_START_WEBHOOK")),
    )
    if config.TEST_EMAIL_TO:
        LOGGER.info('发送测试邮件')
        emailtools.send(
            config.TEST_EMAIL_TO,
            f'[启动] - {_format_time(datetime.now())}',
            '服务启动测试邮件',
        )
    live.connect_all_LiveDanmaku(*_iterate_rooms())
    LOGGER.info('未配置要监控的直播间，请查看 README.md')
