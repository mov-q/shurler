from shurler.tests import *

class TestRedirController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='redir', action='index'))
        # Test response...
