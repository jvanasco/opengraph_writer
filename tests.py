import unittest


from opengraph_writer import OpenGraphItem


class TestsSimple(unittest.TestCase):

    def test_set(self):
        a = OpenGraphItem()
        a.set('og:title', 'MyWebsite')
        a.set('og:type', 'article')

    def test_set_many(self):
        a = OpenGraphItem()
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('article:author', 'abc'),
            ('article:published_time', '2012-01-10')
        ))

    def test_set_and_set_many(self):
        a = OpenGraphItem()
        a.set('og:title', 'MyWebsite')
        a.set('og:type', 'article')
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('article:author', 'abc'),
            ('article:published_time', '2012-01-10')
        ))

    def test_validate_pass(self):
        a = OpenGraphItem()
        a.set('og:title', 'MyWebsite')
        a.set('og:type', 'article')
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('article:author', 'abc'),
            ('article:published_time', '2012-01-10')
        ))
        status = a.validate()
        assert status is True

    def test_validate_fail(self):
        a = OpenGraphItem()
        a.set('og:title', 'MyWebsite')
        # missing og_type, which is required
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('article:author', 'abc'),
            ('article:published_timre', '2012-01-10')
        ))
        status = a.validate()
        assert status is False

    def test_set_multi(self):
        a = OpenGraphItem()
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('og:title', 'MyWebsite'),
            ('og:type', 'article'),
        ))
        a.set('og:tag', 'One', append=True)
        a.set('og:tag', 'Two', append=True)
        a.set('og:tag', 'Three', append=True)
        status = a.validate()
        assert status is True
        as_html = a.as_html()
        assert as_html == """<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:tag" content="One"/>
<meta property="og:tag" content="Two"/>
<meta property="og:tag" content="Three"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>"""

    def test_html(self):
        a = OpenGraphItem()
        a.set('og:title', 'MyWebsite')
        a.set('og:type', 'article')
        a.set('og:description', 'one two three four ? <open >close')
        a.set_many((
            ('og:url', 'http://f.me'),
            ('og:image', 'http://f.me/a.png'),
            ('article:author', 'abc'),
            ('article:published_time', '2012-01-10')
        ))
        status = a.validate()
        assert status is True
        as_html = a.as_html()
        assert as_html == """<meta property="article:author" content="abc"/>
<meta property="article:published_time" content="2012-01-10"/>
<meta property="og:description" content="one two three four ? &lt;open &gt;close"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>"""
