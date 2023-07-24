"""Send email notification when bilibili live start. """
import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Tuple

from bilibili_api import live

from . import config, emailtools, room, webhook, rate_limit

from collections import defaultdict, OrderedDict


def _format_time(v: datetime) -> str:
    return v.strftime("%H:%M:%S %Y-%m-%d")


LOGGER = logging.getLogger(__name__)


async def _handle_live(event):
    rid = event["room_display_id"]

    # TODO: support template for email subject and body
    now = datetime.now()
    room_data = await room.get(rid)
    emailtools.send(
        config.get_room_email_to(rid),
        f'[开播]{room_data["name"]} - {_format_time(now)}',
        f'{room_data["url"]} ',
    )


async def _handle_view(event):
    rid = event["room_display_id"]
    room.ROOM_POPUPARITY[rid] = event["data"]


EVENT_EXAMPLE = {}


def _load_event_example():
    with open("event.example.json", encoding="utf8") as f:
        return json.load(f)


def _save_event_example():
    with open("event.example.json", "w", encoding="utf8") as f:
        json.dump(EVENT_EXAMPLE, f, ensure_ascii=False, indent=2)


try:
    EVENT_EXAMPLE = _load_event_example()
except OSError:
    pass


def _collect_event_example(event):
    event_type = event["type"]
    is_new = event_type not in EVENT_EXAMPLE
    EVENT_EXAMPLE[event_type] = event
    if is_new:
        LOGGER.info("update ./event.example.json due to new event type: %s", event_type)
        _save_event_example()


ROOM_EVENT_TIME: Dict[Tuple[str, str], float] = {}


def _throttle_event(event) -> bool:
    event_type = event["type"]
    rid = str(event["room_display_id"])
    event_time_key = (rid, event_type)
    if event_time_key in ROOM_EVENT_TIME and time.time() - ROOM_EVENT_TIME[
        event_time_key
    ] < int(config.get(f"BILIBILI_EVENT_THROTTLE_{event_type}") or "0"):
        LOGGER.info("event throttled: %s: %s", rid, event_type)
        return True
    ROOM_EVENT_TIME[event_time_key] = time.time()
    return False


ROOM_EVENT_TYPE_KEYS = defaultdict(lambda: defaultdict(OrderedDict))


def _distinct_event(event, data: dict) -> bool:
    event_type = event["type"]
    rid = str(event["room_display_id"])
    key = config.get(f"BILIBILI_EVENT_DISTINCT_KEY_{event_type}", data)
    if key == "":
        return False
    event_keys = ROOM_EVENT_TYPE_KEYS[rid][event_type]
    if key in event_keys:
        LOGGER.info(
            "skip duplicated event: %s: %s: %s",
            rid,
            event_type,
            key,
        )
        return True

    event_keys[key] = True
    limit = int(
        config.get(f"BILIBILI_EVENT_DISTINCT_LIMIT_{event_type}", data) or "128",
    )
    while len(event_keys) > limit >= 0:
        event_keys.popitem(last=False)

    return False


async def _handle_event(event, *, skip_room_data_update=False):
    event_type = event["type"]
    rid = str(event["room_display_id"])

    if event_type == "LIVE":
        LOGGER.info(event)
    else:
        LOGGER.debug(event)

    _collect_event_example(event)

    if _throttle_event(event):
        return

    # update room data cache
    if not skip_room_data_update and event_type in ("LIVE", "PREPARING", "ROOM_CHANGE"):
        room_data = await room.get(rid, max_age_secs=0)

    if event_type == "LIVE":
        await _handle_live(event)
    elif event_type == "VIEW":
        await _handle_view(event)

    room_data = await room.get(rid)
    data = {
        **dict(
            event=event,
            room=room_data,
        ),
        **dict(config.get_items(f"BILIBILI_ROOM_TEMPLATE_VAR_{rid}_")),
    }

    if _distinct_event(event, data):
        return

    await webhook.trigger_many(
        (
            config.get_csv(f"BILIBILI_ROOM_WEBHOOK_{rid}_{event_type}")
            or config.get_csv(f"BILIBILI_WEBHOOK_{event_type}")
        ),
        data,
    )


async def _subscribe(id: str) -> None:
    room1 = live.LiveDanmaku(id)  # type: ignore
    room1.add_event_listener("ALL", _handle_event)  # type: ignore

    while True:
        await room1.connect()
        if room1.get_status() == room1.STATUS_ESTABLISHED:
            await room1.disconnect()


async def _poll(id: str, interval_secs: int) -> None:
    last_is_live = False
    while True:
        await asyncio.sleep(0)
        try:
            data = await room.get(id, max_age_secs=0)
            is_live = data["data"]["room_info"]["live_status"] == 1
            if is_live and not last_is_live:
                now = int(time.time())
                await _handle_event(
                    {
                        "room_display_id": id,
                        "room_real_id": int(id),
                        "type": "LIVE",
                        "data": {
                            "cmd": "LIVE",
                            "is_report": False,
                            "live_key": "",
                            "live_model": 0,
                            "live_platform": "",
                            "live_time": now,
                            "msg_id": "polling-based-live-%s" % (now,),
                            "roomid": int(id),
                            "send_time": now,
                            "sub_session_key": "",
                            "voice_background": "",
                        },
                    },
                    skip_room_data_update=True,
                )
            last_is_live = is_live
        except:
            logging.exception("error during polling")
        await asyncio.sleep(interval_secs)


async def main():
    os.environ.setdefault("BILIBILI_EVENT_THROTTLE_LIVE", "600")
    rate_limit.BILIBILI_API.set(rate_limit.RateLimiter(50, 1))

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(levelname)-6s[%(asctime)s]:%(name)s:%(lineno)d: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    debug_logger_names = config.get_csv("DEBUG")
    for logger in [LOGGER, webhook.LOGGER, room.LOGGER]:
        logger.setLevel(
            logging.DEBUG if logger.name in debug_logger_names else logging.INFO
        )
        logger.addHandler(handler)

    await webhook.trigger_many(config.get_csv("SERVER_WEBHOOK_START"))
    if config.TEST_EMAIL_TO:
        LOGGER.info("发送测试邮件")
        emailtools.send(
            config.TEST_EMAIL_TO,
            f"[启动] - {_format_time(datetime.now())}",
            "服务启动测试邮件",
        )

    def jobs():
        room_ids = list(config.discover_bilibili_room_id())
        if config.POLLING_INTERVAL_SECS > 0:
            for i in room_ids:
                yield _poll(i, config.POLLING_INTERVAL_SECS)

        for i in room_ids:
            yield _subscribe(i)

    await asyncio.gather(*jobs())  # type: ignore
    LOGGER.info("未配置要监控的直播间，请查看 README.md")


if __name__ == "__main__":
    asyncio.run(main())
