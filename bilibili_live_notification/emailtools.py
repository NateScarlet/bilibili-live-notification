"""Send email."""
import email
import smtplib

from . import config


def send_to(to_addrs: list, subject: str, payload: str, ):
    """Send a mail.

    Args:
        to_addrs (list): To address.
        subject (str): Mail subject.
        payload (str): Mail payload.
    """

    msg = email.message.Message()
    msg['From'] = email.utils.formataddr(
        ('哔哩哔哩开播提醒', config.EMAIL_FROM),
    )
    msg['To'] = ','.join(to_addrs)
    msg['Subject'] = subject
    msg.add_header("Sender", config.EMAIL_FROM)
    msg.set_payload(payload)
    msg.set_charset('utf-8')

    session = smtplib.SMTP_SSL(
        host=config.EMAIL_HOST,
        port=config.EMAIL_PORT)
    session.ehlo(config.EMAIL_HOST)
    session.login(
        user=config.EMAIL_USER,
        password=config.EMAIL_PASSWORD)
    session.sendmail(
        from_addr=config.EMAIL_USER,
        to_addrs=to_addrs,
        msg=msg.as_bytes())
    session.quit()

def send(subject: str, payload: str):
    """Send email to config specifield addresses.  """
    send_to(config.EMAIL_TO, subject, payload)
