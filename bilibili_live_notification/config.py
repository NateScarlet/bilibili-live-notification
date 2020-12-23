"""application config. """
import os


def _getenv_csv(name: str) -> list:
    return [i for i in (os.getenv(name) or "").split(",") if i]


EMAIL_FROM = os.getenv("EMAIL_FROM") or "bilibili-live-notification@noreply.example.com"
EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.qq.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or "465")
EMAIL_USER = os.getenv("EMAIL_USER") or "example@qq.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or "<email password>"
EMAIL_TO = _getenv_csv("EMAIL_TO")
TEST_EMAIL_TO = _getenv_csv("TEST_EMAIL_TO")
BILIBILI_ROOM_ID = set(int(i) for i in _getenv_csv("BILIBILI_ROOM_ID"))


def get_room_name(room_display_id: str) -> str:
    """try return `BILIBILI_ROOM_NAME_{id}` config , and fallback to id itself.

    Args:
        room_display_id (str): Room display id

    Returns:
        list: NAME config for this room.
    """

    return os.getenv(f'BILIBILI_ROOM_NAME_{room_display_id}') or room_display_id


def get_room_email_to(room_display_id: str) -> list :
    """try return `BILIBILI_ROOM_EMAIL_TO_{id}` config , and fallback to EMAIL_TO.

    Args:
        room_display_id (str): Room display id

    Returns:
        list: EMAIL_TO config for this room.
    """

    return _getenv_csv(f"BILIBILI_ROOM_EMAIL_TO_{room_display_id}") or EMAIL_TO
