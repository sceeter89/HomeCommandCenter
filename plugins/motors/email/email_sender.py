from configparser import ConfigParser
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
import smtplib
from api.motor import Motor

UNEXPECTED_TERMINATION_SUBJECT = "Command Center - Terminating"
UNEXPECTED_TERMINATION_BODY = """Beware!
Plugin '{key}' requested application shutdown. It's type is: '{type}'.

Reason provided by plugin:
{reason}
"""

ALARM_ON_ALERT_SUBJECT = "Command Center - Alarm Alert!"
ALARM_ON_ALERT_BODY = """Attention!
Something just triggered alarm alert at {now}. We tried to attach all information that we posses about situation:
Home state:
{state}

If any webcam was attached then you will find picture attached.
"""

class EmailSender(Motor):
    def __init__(self):
        super().__init__()
        config = ConfigParser()
        config.read('/etc/myhome/email.ini')
        self.host = config.get('email', 'smtp')
        self.username = config.get('email', 'username')
        self.password = config.get('email', 'password')
        self.port = config.get('email', 'port')
        self.origin = \
            formataddr((str(Header(config.get('email', 'display_name'), 'utf-8')), config.get('email', 'sender_email')))
        self.recipients = config.get('email', 'recipients').split(';')
        self.holiday_recipients = config.get('email', 'holiday_recipients').split(';')
        self.alarm_previous_armed = False
        self.alarm_previous_alert = False

    def _open_smtp_connection(self):
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.login(self.username, self.password)
        return smtp

    def send_plain_text_mail(self, subject, body, holiday_mode):
        if holiday_mode:
            recipients = self.recipients + self.holiday_recipients
        else:
            recipients = self.recipients

        try:
            smtp = self._open_smtp_connection()
            for recipient in recipients:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = self.origin
                    msg['To'] = recipient
                    msg_body = MIMEText(body, 'plain')
                    msg.attach(msg_body)
                    smtp.sendmail(self.origin, recipient, msg.as_string())
                except Exception as e:
                    logging.exception('Failed to send plain text e-mail to ' + recipient, exc_info=e)
            smtp.quit()
        except Exception as e:
            logging.exception('Unexpected error', exc_info=e)

    def on_trigger(self, current_state):
        holiday_mode = "user-settings" in current_state and current_state["user-settings"]["holiday-mode"]
        alarm_alert = "alarm" in current_state and current_state["alarm"]["alert"]
        alarm_armed = "alarm" in current_state and current_state["alarm"]["armed"]

        if "termination" in current_state:
            term_info = current_state["termination"]
            if term_info[0]:
                body = UNEXPECTED_TERMINATION_BODY.format(key=term_info[0], type=repr(term_info[1]),
                                                          reason=term_info[2])
                self.send_plain_text_mail(UNEXPECTED_TERMINATION_SUBJECT, body, holiday_mode)

        if not self.alarm_previous_alert and alarm_alert:
            self.send_plain_text_mail(ALARM_ON_ALERT_SUBJECT, ALARM_ON_ALERT_BODY, holiday_mode)

        self.alarm_previous_alert = alarm_alert
