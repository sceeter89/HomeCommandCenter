from configparser import ConfigParser
from api.motor import Motor


class EmailSender(Motor):
    def __init__(self):
        config = ConfigParser()
        config.read('/etc/myhome/email.ini')
        self.host = config.get('email', 'smtp')
        self.username = config.get('email', 'username')
        self.password = config.get('email', 'password')
        self.port = config.get('email', 'port')
        self.origin = self.username