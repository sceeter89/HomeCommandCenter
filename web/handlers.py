from tornado.web import RequestHandler

class BaseHandler(RequestHandler):
    pass

class AppHandler(BaseHandler):
    def get(self):
        self.render('index.html')
