opengraph_writer
================

![Python package](https://github.com/jvanasco/opengraph_writer/workflows/Python%20package/badge.svg)

About
=====

This library was created to both manage writing OpenGraph data, and perform
lightweight verifications for offline debugging.

This library does the following:

- CREATE an object to stash OGP data
- VALIDATE the data, offering debug information on the object
- RENDER the object as html, and optionally include debug data on incorrect elements

Each `OpenGraphItem` represents one object. A property can have multiple
values, such as several images for the same page.

Most of the validation routines were derived from regexing the `https://ogp.me`
site into a Python dict, and researching what they are supposed to do.
The validation routes themselves are super trivial.

At the time of initially writing this library, and several checks ever since, the
specification on  the `https://ogp.me` seems out of date. 

In practice, Facebook's "premier" partners seem to all be using URLs which point 
to certain data , however there aren't any guidelines for this within the
public OGP spec.

An example would be on the Spotify integration: when looking at a `SONG`, the
`ARTIST` and `ALBUM` refer to URLs which contain the relevant data.

Documentation
=============

The Python file contains extensive inline documentation.

### Multiple images

Use `append=True` to add another value to the same property. Each image is
validated individually, and the rendered tags keep the order in which the
images were added.

```python
from opengraph_writer import OpenGraphItem

item = OpenGraphItem(
    [
        ("og:title", "Example page"),
        ("og:type", "website"),
        ("og:url", "https://example.com/page"),
        ("og:image", "https://example.com/cover.jpg"),
    ]
)
item.set("og:image", "https://example.com/detail.jpg", append=True)

if item.validate():
    print(item.as_html())
```


Contributions Welcome!
======================

The test matrix covers CPython 3.6 through 3.15. Run the tests for your
active Python interpreter with `tox -e py`. The run writes its HTML coverage
report to `htmlcov/index.html`.


Framework Support: Pyramid
==========================

This package offers an includeme for Pyramid to set up an `opengraph_item`
as a `@reify` request method.

Simply update your application:

	config.include("opengraph_writer.pyramid_helpers")

And your `Request` objects will be extended as such:

    request.opengraph_item
    
    
    

