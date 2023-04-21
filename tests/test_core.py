# stdlib
import datetime
import unittest

# local package
from opengraph_writer import OpenGraphItem


class _TestsHelper(object):
    def _make_core_compliant(
        self,
        og_title="MyWebsite",
        og_type="website",
    ):
        a = OpenGraphItem()
        a.set_many(
            (
                ("og:title", og_title),
                ("og:type", og_type),
                ("og:image", "http://f.me/a.png"),
                ("og:url", "http://f.me"),
            )
        )
        return a


class TestsSimple(unittest.TestCase, _TestsHelper):
    def test_main(self):
        # this was in the core package as if __main__:
        a = OpenGraphItem()
        a.set("og:title", "MyWebsite")
        a.set("og:type", "article")
        a.set_many(
            (
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
                ("og:image", "http://f.me/a.png"),
                ("og:url", "http://f.me"),
            )
        )
        _status = a.validate()
        self.assertTrue(_status)
        _as_html = a.as_html(debug=True)
        self.assertEqual(
            _as_html,
            """<meta property="article:author" content="abc"/>
<meta property="article:published_time" content="2012-01-10"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_set(self):
        # ensure we can `set` by doing all the REQUIRED elements
        a = OpenGraphItem()
        a.set("og:image", "http://f.me/a.png")
        a.set("og:title", "MyWebsite")
        a.set("og:type", "article")
        a.set("og:url", "http://f.me")
        _status = a.validate()
        self.assertTrue(_status)
        _as_html = a.as_html(debug=True)
        self.assertEqual(
            _as_html,
            """<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_set_many(self):
        # ensure we can `set_many` by doing all the REQUIRED elements
        a = OpenGraphItem()
        a.set_many(
            (
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
                ("og:image", "http://f.me/a.png"),
                ("og:url", "http://f.me"),
            )
        )

    def test_set_and_set_many(self):
        a = OpenGraphItem()
        a.set("og:title", "MyWebsite")
        a.set("og:type", "article")
        a.set_many(
            (
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
                ("og:image", "http://f.me/a.png"),
                ("og:url", "http://f.me"),
            )
        )

    def test_validate_pass(self):
        a = OpenGraphItem()
        a.set("og:title", "MyWebsite")
        a.set("og:type", "article")
        a.set_many(
            (
                ("og:url", "http://f.me"),
                ("og:image", "http://f.me/a.png"),
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
            )
        )
        status = a.validate()
        self.assertTrue(status)

        errors = a.errors()
        self.assertFalse(errors["critical"])
        self.assertFalse(errors["not_validated"])
        for subtype in (
            "article:modified_time",
            "article:expiration_time",
            "article:section",
            "article:tag",
        ):
            self.assertIn(subtype, errors["recommended"])
            self.assertEqual(
                "non-required subtype not included", errors["recommended"][subtype]
            )

        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="article:author" content="abc"/>
<meta property="article:published_time" content="2012-01-10"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_validate_fail(self):
        a = OpenGraphItem()
        # missing og_type, which is required
        a.set_many(
            (
                ("og:title", "MyWebsite"),
                ("og:url", "http://f.me"),
                ("og:image", "http://f.me/a.png"),
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
            )
        )
        status = a.validate()
        self.assertFalse(status)

        errors = a.errors()
        self.assertTrue(errors["critical"])
        self.assertIn("og:type", errors["critical"])
        self.assertEqual(errors["critical"]["og:type"], "Missing og:type")
        self.assertFalse(errors["recommended"])
        self.assertTrue(errors["not_validated"])
        self.assertCountEqual(
            errors["not_validated"], ["article:published_time", "article:author"]
        )

        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="article:author" content="abc"/>
<meta property="article:published_time" content="2012-01-10"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_set_multi(self):
        a = OpenGraphItem()
        a.set_many(
            (
                ("og:url", "http://f.me"),
                ("og:image", "http://f.me/a.png"),
                ("og:title", "MyWebsite"),
                ("og:type", "article"),
            )
        )
        a.set("og:tag", "One", append=True)
        a.set("og:tag", "Two", append=True)
        a.set("og:tag", "Three", append=True)
        status = a.validate()
        self.assertTrue(status)
        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:tag" content="One"/>
<meta property="og:tag" content="Two"/>
<meta property="og:tag" content="Three"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_html(self):
        a = OpenGraphItem()
        a.set("og:title", "MyWebsite")
        a.set("og:type", "article")
        a.set("og:description", "one two three four ? <open >close")
        a.set_many(
            (
                ("og:url", "http://f.me"),
                ("og:image", "http://f.me/a.png"),
                ("article:author", "abc"),
                ("article:published_time", "2012-01-10"),
            )
        )
        status = a.validate()
        self.assertTrue(status)
        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="article:author" content="abc"/>
<meta property="article:published_time" content="2012-01-10"/>
<meta property="og:description" content="one two three four ? &lt;open &gt;close"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyWebsite"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )


class Tests_DataTypes(unittest.TestCase, _TestsHelper):
    def test_enum__valid(self):
        a = self._make_core_compliant(
            og_title="MyProfile",
            og_type="profile",
        )
        a.set("profile:gender", "male")
        status = a.validate()
        self.assertTrue(status)
        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyProfile"/>
<meta property="og:type" content="profile"/>
<meta property="og:url" content="http://f.me"/>
<meta property="profile:gender" content="male"/>""",
        )

    def test_enum__invalid(self):
        a = self._make_core_compliant(
            og_title="MyProfile",
            og_type="profile",
        )
        a.set("profile:gender", "ai")
        status = a.validate()
        self.assertTrue(status)  # `profile:gender` is not a required element
        _errors = a.errors()
        self.assertIn("profile:gender", _errors["recommended"])
        self.assertEqual(
            _errors["recommended"]["profile:gender"],
            "non-required subtype does not validate correctly",
        )

        for subtype in (
            "profile:first_name",
            "profile:last_name",
            "profile:username",
        ):
            self.assertIn(subtype, _errors["recommended"])
            self.assertEqual(
                _errors["recommended"][subtype],
                "non-required subtype not included",
            )

        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyProfile"/>
<meta property="og:type" content="profile"/>
<meta property="og:url" content="http://f.me"/>
<meta property="profile:gender" content="ai"/>""",
        )

    def test_datetime__valid(self):
        a = self._make_core_compliant(
            og_title="MyArticle",
            og_type="article",
        )
        a.set("article:published_time", datetime.datetime(2021, 1, 10))
        status = a.validate()
        self.assertTrue(status)
        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="article:published_time" content="2021-01-10T00:00:00"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyArticle"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )

    def test_date__valid(self):
        a = self._make_core_compliant(
            og_title="MyArticle",
            og_type="article",
        )
        a.set("article:published_time", datetime.date(2021, 1, 1))
        status = a.validate()
        self.assertTrue(status)
        as_html = a.as_html()
        self.assertEqual(
            as_html,
            """<meta property="article:published_time" content="2021-01-01"/>
<meta property="og:image" content="http://f.me/a.png"/>
<meta property="og:title" content="MyArticle"/>
<meta property="og:type" content="article"/>
<meta property="og:url" content="http://f.me"/>""",
        )
