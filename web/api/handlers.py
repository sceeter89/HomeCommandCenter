from tornado.web import RequestHandler


class BaseApiHandler(RequestHandler):
    pass


class ApiLedHandler(BaseApiHandler):
    pass


class ApiMessageHandler(BaseApiHandler):
    pass


class ApiBacklightHandler(BaseApiHandler):
    pass


class ApiAlarmHandler(BaseApiHandler):
    pass


class ApiStatusHandler(BaseApiHandler):
    pass
