#!/usr/bin/env python3.2
import logging

from tornado.escape import json_decode, json_encode
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.options import define, options, parse_command_line, parse_config_file
from tornado.web import Application, RequestHandler, authenticated
from web.api.handlers import ApiLedHandler, ApiMessageHandler, ApiBacklightHandler, ApiAlarmHandler, ApiStatusHandler
from web.handlers import AppHandler

define('port', default=8888, help="port to listen on")
define('config_file', default='settings.config',
        help='filename for additional configuration')
define('debug', default=False, group='application',
        help="run in debug mode (with automatic reloading)")

def main():
    parse_command_line(final=False)
    parse_config_file(options.config_file)
    app = Application(
            [
                ('/', AppHandler),
                ('/api/led/(?P<color>[a-zA-Z]+)/?(?P<state>[01])?', ApiLedHandler),
                ('/api/display/message', ApiMessageHandler),
                ('/api/display/backlight/?(?P<state>[01])?', ApiBacklightHandler),
                ('/api/alarm/(?P<property>[a-zA-Z]+)', ApiAlarmHandler),
                ('/api/status', ApiStatusHandler),
                ],
            #login_url='/login',
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            **options.group_dict('application'))
    app.listen(options.port)
    logging.info('Listening on http://localhost:%d' % options.port)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
