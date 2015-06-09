from configparser import ConfigParser
from datetime import datetime
import logging
import requests

from api.motor import Motor

ALARM_ON_ALERT_MESSAGE = "Command Center - Alarm is now on alert! Alert start time: %s"

ALARM_ON_ALERT_OFF_MESSAGE = "Command Center - Alarm alert is off. Stop time: %s"


class SmsSender(Motor):
    def __init__(self):
        super().__init__()
        config = ConfigParser()
        config.read('/etc/command_center/sms.ini')
        self.username = config.get('sms', 'username')
        self.password = config.get('sms', 'password')
        self.api_url = config.get('sms', 'api_url')
        self.recipients = config.get('sms', 'recipients').split(';')
        self.holiday_recipients = config.get('sms', 'holiday_recipients').split(';')
        self.alarm_previous_alert = False

    def _send_messages(self, text, holiday_mode):
        if holiday_mode:
            recipients = self.recipients + self.holiday_recipients
        else:
            recipients = self.recipients
        logging.debug('Sending SMSes to: ' + repr(recipients))

        for recipient in recipients:
            try:
                payload = {'sandbox': '0', 'login': self.username, 'pass': self.password, 'recipient': recipient,
                           'message': text, 'msg_type': 3}
                r = requests.get(self.api_url, params=payload, verify=False).text
                if r.startswith('ERR'):
                    logging.error('Failed to send sms: ' + r)
                else:
                    logging.debug('Successfully sent SMS: ' + r)
            except Exception as e:
                logging.exception('Failed to send SMS to ' + recipient, exc_info=e)

    def on_trigger(self, current_state):
        holiday_mode = "user-settings" in current_state and current_state["user-settings"]["holiday-mode"]
        alarm_alert = "alarm" in current_state and current_state["alarm"]["alert"]

        if not self.alarm_previous_alert and alarm_alert:
            self._send_messages(ALARM_ON_ALERT_MESSAGE % str(datetime.now()), holiday_mode)
        elif self.alarm_previous_alert and not alarm_alert:
            self._send_messages(ALARM_ON_ALERT_OFF_MESSAGE % str(datetime.now()), holiday_mode)
        self.alarm_previous_alert = alarm_alert
