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