as posted on https://www.facebook.com/groups/opengraph/

I started to build a python library to both manage writing open graph data, and do some lightweight verifications for offline debugging.

it currently does the following:
- create an object to stash ogp data
- validate the data , offering debug information on the object
- print out the object as html, and optionally include debug data on the wrong elements

it works on simple page data, but i haven't time/energy/a-need to handle things like storing multi-value items (ie, multiple profiles or tracks for a page) , or validating them.

Most of the work was just regexing the ogp.me site into a python dict and researching what its supposed to do. The validations themselves are super trivial.

The spec on ogp.me also seems out of date -- in practice, Facebook's "premier" partners seem to all be using URLs to point to certain data , however there aren't any guidelines for this listed. An example would be on the Spotify integration: when looking at a SONG, the ARTIST and ALBUM refer to URLs that contain the relevant data.

anyways, if anyone wants to fork and tackle the multiple value problem, please do.

Also, there are actual docs within the python file...


=============


v 0.1.0

Goal:

i need a lightweight package that can do the following:

1. create an object to store open graph metadata for a url
2. store that object, and bring it back to continually populate and eventually print during page generation
3. validate itself at least trivially, so i don't have to do dns tricks to let the facebook linter/debugger work wherever i am

to do:

1. object needs proper array/multivalue support
2. object needs validation on profile
3. in practice, but not docs, a lot of the ogp values will accept url that create a network. ie: song links to album, and musician pages.  this validation isn't supported.


recently done:

1. consolidate documentation on open graph 1.0 and 2.0
2. create structured data describing the open graph protocls
3. create an object that can store og data , validate itself, and print itself out
4. create some helpers for pyramid and pylons(removed in 0.3.0)

Example Usage:

    a = OpenGraphItem()
    a.set('og:title','MyWebsite')
    a.set('og:type','article')
    a.set_many( (('og:url','http://f.me'),('og:image','http://f.me/a.png'),('article:author','abc'),('article:published_time','2012-01-10')) )
    status = a.validate()
    if status:
       print "object ok"
    else:
       print "object not ok"
    print a.as_html(debug=True)

Notes:

the debug=True argument will print debugging info on your object. isn't that special!


# pyramid

this package now has an includeme for pyramid to set up an opengraph_item as a reify'd request method



-- old method below --
in pyramid you might do:

	from opengraph_writer import pyramid_opengraph_item
	class handler(handler)
		def setup_method(self,request):
			og= pyramid_opengraph_item(request)
			og.set('og:type','website')
			og.set('og:site_name','Cliqued.in')

then in your mako templates...

	${request.pyramid_opengraph_item.as_html()|n}


