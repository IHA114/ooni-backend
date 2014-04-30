import socket
import json

from twisted.internet import reactor, defer
from twisted.trial import unittest

from cyclone import httpclient


def random_unused_port(bind_address='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

reports = {}


def mock_initialize(self):
    self.report_dir = '.'
    self.archive_dir = '.'
    self.reports = reports
    self.policy_file = None
    self.helpers = {}
    self.stale_time = 10


class HandlerTestCase(unittest.TestCase):
    app = None
    _port = None
    _listener = None

    @property
    def port(self):
        if not self._port:
            self._port = random_unused_port()
        return self._port

    def setUp(self, *args, **kw):
        if self.app:
            self._listener = reactor.listenTCP(self.port, self.app)
        return unittest.TestCase.setUp(self, *args, **kw)

    def tearDown(self):
        if self._listener:
            for report in reports.values():
                try:
                    report.delayed_call.cancel()
                except:
                    pass
            self._listener.stopListening()

    @defer.inlineCallbacks
    def request(self, path, method="GET", postdata=None):
        url = "http://localhost:%s%s" % (self.port, path)
        if isinstance(postdata, dict):
            postdata = json.dumps(postdata)

        response = yield httpclient.fetch(url, method=method,
                                          postdata=postdata)
        defer.returnValue(response)
