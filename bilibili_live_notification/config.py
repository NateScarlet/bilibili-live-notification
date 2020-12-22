import os

EMAIL_FROM = os.getenv("EMAIL_FROM") or "noreply@example.com"
EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.qq.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or "465")
EMAIL_USER = os.getenv("EMAIL_USER") or "example@qq.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or "<email password>"
EMAIL_TO = (os.getenv("EMAIL_TO") or "").split(",")
BILIBILI_ROOM_ID = set(int(i) for i in (os.getenv("BILIBILI_ROOM_ID") or "").split(","))
