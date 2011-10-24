import pickle

from nose.tools import istest
import redis
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from pycket.session import SessionManager, SessionMixin


class FunctionalTest(AsyncHTTPTestCase):
    bucket = None

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.bucket.flushall()

    def get_app(self):
        if self.bucket is None:
            self.bucket = redis.Redis(db=SessionManager.DB)
        class SimpleHandler(RequestHandler, SessionMixin):
            def get(self):
                self.session.set('foo', 'bar')
                self.write(self.session.get('foo'))

            def get_secure_cookie(self, *args, **kwargs):
                return 'some-generated-cookie'

        return Application([
            (r'/', SimpleHandler),
        ], **{
            'cookie_secret': 'Python rocks!',
        })

    @istest
    def works_with_request_handlers(self):
        self.assertEqual(len(self.bucket.keys()), 0)

        response = self.fetch('/')

        self.assertEqual(response.code, 200)
        self.assertIn('bar', response.body)

        self.assertEqual(len(self.bucket.keys()), 1)