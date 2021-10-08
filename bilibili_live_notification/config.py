"""application config. """
import os
from datetime import datetime
from typing import Iterator, Optional, Tuple

import jinja2


class _ChainableDebugUndefined(jinja2.ChainableUndefined, jinja2.DebugUndefined):
    pass


def get(name: str, data: Optional[dict] = None) -> str:
    """get string config

    Args:
        name (str): env var name
        data (Optional[dict], optional): template variables. Defaults to None.

    Returns:
        str: rendered config value
    """

    value = os.getenv(name) or ""
    var_prefix = "TEMPLATE_VAR_"
    if name.startswith(var_prefix):
        return value
    return jinja2.Template(value, undefined=_ChainableDebugUndefined,).render(
        **{
            **dict(datetime=datetime),
            **dict(get_items(var_prefix, data)),
            **(data or {}),
        },
    )


def parse_csv(v: Optional[str]) -> list:
    """parse comma separated values.

    Args:
        v (Optional[str]): value

    Returns:
        list: values
    """
    return [i for i in (v or "").split(",") if i]


def get_csv(name: str, data: Optional[dict] = None) -> list:
    """get csv config

    Args:
        name (str): env var name
        data (Optional[dict], optional): template variables. Defaults to None.

    Returns:
        list: values
    """
    return parse_csv(get(name, data))


def get_items(prefix: str, data: Optional[dict] = None) -> Iterator[Tuple[str, str]]:
    """get room id from env vars that has BILIBILI_ROOM_NAME_ prefix

    Yields:
        Iterator[str]: room ids.
    """
    for i in os.environ.keys():
        if i.startswith(prefix):
            yield i[len(prefix) :], get(i, data)


EMAIL_FROM = get("EMAIL_FROM") or "bilibili-live-notification@noreply.github.com"
EMAIL_HOST = get("EMAIL_HOST") or "smtp.qq.com"
EMAIL_PORT = int(get("EMAIL_PORT") or "465")
EMAIL_USER = get("EMAIL_USER") or "example@qq.com"
EMAIL_PASSWORD = get("EMAIL_PASSWORD") or "<email password>"
EMAIL_TO = parse_csv(get("EMAIL_TO"))
TEST_EMAIL_TO = parse_csv(get("TEST_EMAIL_TO"))
BILIBILI_EMAIL_THROTTLE = int(get("BILIBILI_EMAIL_THROTTLE") or "600")


def discover_bilibili_room_id() -> Iterator[str]:
    """get room id from env vars that has BILIBILI_ROOM_NAME_ prefix

    Yields:
        Iterator[str]: room ids.
    """
    prefix = "BILIBILI_ROOM_NAME_"
    for i in os.environ.keys():
        if i.startswith(prefix):
            yield i[len(prefix) :]


def get_room_name(room_display_id: str) -> str:
    """try return `BILIBILI_ROOM_NAME_{id}` config , and fallback to id itself.

    Args:
        room_display_id (str): Room display id

    Returns:
        str: NAME config for this room.
    """

    return os.getenv(f"BILIBILI_ROOM_NAME_{room_display_id}") or room_display_id


def get_room_email_to(room_display_id: str) -> list:
    """try return `BILIBILI_ROOM_EMAIL_TO_{id}` config , and fallback to EMAIL_TO.

    Args:
        room_display_id (str): Room display id

    Returns:
        list: EMAIL_TO config for this room.
    """

    return parse_csv(get(f"BILIBILI_ROOM_EMAIL_TO_{room_display_id}")) or EMAIL_TO
