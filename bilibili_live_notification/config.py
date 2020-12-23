import os


def _getenv_csv(name: str) -> list:
    return [i for i in (os.getenv(name) or "").split(",") if i]


EMAIL_FROM = os.getenv("EMAIL_FROM") or "noreply@example.com"
EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.qq.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or "465")
EMAIL_USER = os.getenv("EMAIL_USER") or "example@qq.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or "<email password>"
EMAIL_TO = _getenv_csv("EMAIL_TO")
TEST_EMAIL_TO = _getenv_csv("TEST_EMAIL_TO")
BILIBILI_ROOM_ID = set(int(i) for i in _getenv_csv("BILIBILI_ROOM_ID"))
