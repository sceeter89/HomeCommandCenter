from configparser import ConfigParser
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
import os
from os.path import basename
import smtplib
import subprocess
import time
from api.motor import Motor
from yapsy.IPlugin import IPlugin

UNEXPECTED_TERMINATION_SUBJECT = "Command Center - Terminating"
UNEXPECTED_TERMINATION_BODY = """Beware!
Plugin '{key}' requested application shutdown. It's type is: '{type}'.

Reason provided by plugin:
{reason}

Regards,
Your Home
"""

ALARM_ON_ALERT_SUBJECT = "Command Center - Alarm Alert!"
ALARM_ON_ALERT_BODY = """Attention!
Something just triggered alarm alert at {now}. We tried to attach all information that we posses about situation:
Home state:
{state}

If any webcam was attached then you will find picture attached.

Regards,
Your Home
"""

ALARM_ON_ALERT_OFF_SUBJECT = "Command Center - Alarm Alert - closed"
ALARM_ON_ALERT_OFF_BODY = """Right now alarm alert was turned off, either due to timeout or someone disarmed it.

Regards,
Your Home
"""

ALARM_ON_HOLIDAY_DISARMED_SUBJECT = "Command Center - Alarm disarmed"
ALARM_ON_HOLIDAY_DISARMED_BODY = """Someone just disarmed alarm. It may not be anything alarming, but just in case you are
not aware of that fact consider contact with people that have keys to apartment. If you attached any webcam,
find photos attached.

Regards,
Your Home
"""

ALARM_ON_HOLIDAY_ARMED_SUBJECT = "Command Center - Alarm armed"
ALARM_ON_HOLIDAY_ARMED_BODY = """Just to let you know, alarm is armed again.

Regards,
Your Home
"""


def _take_photo():
    file_path = '/tmp/photo{0}.jpg'.format(time.time())
    subprocess.call(['/usr/bin/fswebcam',
                     '--resolution', '1280x720',
                     '--jpeg', '95',
                     '--title', '"Photography on alert"',
                     '--no-subtitle',
                     '--save', file_path])
    return file_path


class EmailSender(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        config = ConfigParser()
        config.read('/etc/command_center/email.ini')
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

    def _send_plain_text_mail(self, subject, body, holiday_mode, attachments=list()):
        if holiday_mode:
            recipients = self.recipients + self.holiday_recipients
        else:
            recipients = self.recipients

        try:
            smtp = self._open_smtp_connection()
            remove_attachments = True
            for recipient in recipients:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = self.origin
                    msg['To'] = recipient
                    msg_body = MIMEText(body, 'plain')
                    msg.attach(msg_body)

                    for attachment in attachments:
                        with open(attachment, "rb") as f:
                            msg.attach(MIMEApplication(
                                f.read(),
                                Content_Disposition='attachment; filename="%s"' % basename(attachment)
                            ))

                    smtp.sendmail(self.origin, recipient, msg.as_string())
                except Exception as e:
                    logging.exception('Failed to send plain text e-mail to ' + recipient, exc_info=e)
                    logging.error("Following attachments weren't remove: " + repr(attachments))
                    remove_attachments = False
            smtp.quit()
            if remove_attachments:
                for attachment in attachments:
                    os.remove(attachment)
        except Exception as e:
            logging.exception('Unexpected error', exc_info=e)

    def _take_photo_and_send_mail(self, subject, body, holiday_mode):
        try:
            photo1 = _take_photo()
            time.sleep(0.5)
            photo2 = _take_photo()
            self._send_plain_text_mail(subject, body, holiday_mode, [photo1, photo2])
        except Exception as e:
            logging.debug('Failed to attach photos. Sending text-only email.', exc_info=e)
            self._send_plain_text_mail(subject, body, holiday_mode)

    def on_trigger(self, current_state):
        holiday_mode = "user-settings" in current_state and current_state["user-settings"]["holiday-mode"]
        alarm_alert = "alarm" in current_state and current_state["alarm"]["alert"]
        alarm_armed = "alarm" in current_state and current_state["alarm"]["armed"]

        if "termination" in current_state and current_state["termination"]:
            term_info = current_state["termination"]
            if term_info[0]:
                body = UNEXPECTED_TERMINATION_BODY.format(key=term_info[0], type=repr(term_info[1]),
                                                          reason=term_info[2])
                self._send_plain_text_mail(UNEXPECTED_TERMINATION_SUBJECT, body, holiday_mode)

        if not self.alarm_previous_alert and alarm_alert:
            self._take_photo_and_send_mail(ALARM_ON_ALERT_SUBJECT, ALARM_ON_ALERT_BODY, holiday_mode)
        elif self.alarm_previous_alert and not alarm_alert:
            self._send_plain_text_mail(ALARM_ON_ALERT_OFF_SUBJECT, ALARM_ON_ALERT_OFF_BODY, holiday_mode)
        self.alarm_previous_alert = alarm_alert

        if holiday_mode and self.alarm_previous_armed and not alarm_armed:
            self._take_photo_and_send_mail(ALARM_ON_HOLIDAY_DISARMED_SUBJECT, ALARM_ON_HOLIDAY_DISARMED_BODY,
                                           holiday_mode)
        elif holiday_mode and not self.alarm_previous_armed and alarm_armed:
            self._send_plain_text_mail(ALARM_ON_HOLIDAY_ARMED_SUBJECT, ALARM_ON_HOLIDAY_ARMED_BODY, holiday_mode)
        self.alarm_previous_armed = alarm_armed
