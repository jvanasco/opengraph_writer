# stdlib
import unittest

# local package to test
import opengraph_writer

# pyramid testing requirements
from pyramid import testing
from pyramid.interfaces import IRequestExtensions
from webob.multidict import MultiDict


# ==============================================================================


class TestSetupSimple(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        # grab the config object, then modify in place
        settings = self.config.get_settings()
        self.config.include("opengraph_writer.pyramid_helpers")
        self.context = testing.DummyResource()
        self.request = testing.DummyRequest()

        # mare sure we have it...
        exts = self.config.registry.getUtility(IRequestExtensions)
        self.assertTrue("opengraph_item" in exts.descriptors)

        # intiialize a writer for the request
        opengraph_item = exts.descriptors["opengraph_item"].wrapped(self.request)
        # copy the writer onto the request...
        self.request.opengraph_item = opengraph_item

    def tearDown(self):
        testing.tearDown()

    def test_configured(self):
        self.assertIsInstance(
            self.request.opengraph_item, opengraph_writer.OpenGraphItem
        )
