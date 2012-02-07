
"""
v 0.0.3

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
        4. create some helpers for pyramid and pylons
        
Usage:

    a= OpenGraphItem()
    a.set('og:title','MyWebsite')
    a.set('og:type','article')
    a.set_many( (('og:url','http://f.me'),('og:image','http://f.me/a.png'),('article:author','abc'),('article:published_time','2012-01-10')) )
    status = a.validate()
    if status:
       print "object ok"
    else:
       print "object not ok"
    print a.as_html(debug=True)


	the debug=True argument will print debugging info on your object. isn't that special!
	
	
	in pyramid you might do:


		from opengraph_writer import pyramid_opengraph_item
		class handler(handler)
			def setup_method(self,request):
				og= pyramid_opengraph_item(request)
				og.set('og:type','website')
				og.set('og:site_name','Cliqued.in')
		
	then in mako:
		${request.pyramid_opengraph_item.as_html()|n}
		

==============

The followig information about Open Graph 1.0 is copied verbatim from Facebook, and remains their copyright :

    https://developers.facebook.com/docs/opengraphprotocol/

    Example:

         <meta property="og:title" content="The Rock"/>


    The Open Graph protocol defines four required properties:

        og:title - The title of your object as it should appear within the graph, e.g., "The Rock".
        og:type - The type of your object, e.g., "movie". See the complete list of supported types.
        og:image - An image URL which should represent your object within the graph. The image must be at least 50px by 50px and have a maximum aspect ratio of 3:1. We support PNG, JPEG and GIF formats. You may include multiple og:image tags to associate multiple images with your page.
        og:url - The canonical URL of your object that will be used as its permanent ID in the graph, e.g., http://www.imdb.com/title/tt0117500/.

    In addition, we've extended the basic meta data to add a required field to connect your webpage with Facebook:

        fb:app_id - A Facebook Platform application ID that administers this page.

    It's also recommended that you include the following properties as well as these multi-part properties.

        og:site_name - A human-readable name for your site, e.g., "IMDb".
        og:description - A one to two sentence description of your page.

    ...

    To associate the page with your Facebook account, add the additional property fb:admins to your page with a comma-separated list of the user IDs or usernames of the Facebook accounts who own the page, e.g.:

        <meta property="fb:admins" content="USER_ID1,USER_ID2"/>

The following is taken from the 2.0 spec -- http://ogp.me/ , and remains their copyright

Arrays
    If a tag can have multiple values, just put multiple versions of the same <meta> tag on your page. The first tag (from top to bottom) is given preference during conflicts.

        <meta property="og:image" content="http://example.com/rock.jpg" />
        <meta property="og:image" content="http://example.com/rock2.jpg" />

    Put structured properties after you declare their root tag. Whenever another root element is parsed, that structured property is considered to be done and another one is started.


"""
import types
import urllib2
import datetime
import re

# http://en.wikipedia.org/wiki/ISO_8601
regex_dates = {
        ##  Date    2012-02-02
        'date': re.compile('^([0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])$'),

        ## Ordinal date:    2012-033
        'ordinal_date' : re.compile('^([0-9]{4})-(36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9])$'),

        ## Date with week number:   2012-W05-4
        'week_number': re.compile('^([0-9]{4})-?W(5[0-3]|[1-4][0-9]|0[1-9])-?([1-7])$'),

        ## Separate date and time in UTC:   2012-02-02 15:29Z
        'datetime, UTC': re.compile('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$'),
}

## basically just testing that the string starts with http/https, and has some resemeblence of a domain on it.  after an optional trailing slash, i don't need to make this super accurate
regex_url= re.compile("""^http[s]?:\/\/[a-z0-9.\-]+[\.][a-z]{2,4}\/?""")










og_properties = {
    'og:title' : {
        'required':True,
        'description': 'The title of your object as it should appear within the graph, e.g., "The Rock".',
        'type':'string',
    },
    'og:type' : {
        'required':True,
        'description':'The type of your object, e.g., "movie". See the complete list of supported types.',
        'type':'string',
        'valid_types-1' : {
            'activity':{'grouping':'Activities'},
            'sport':{'grouping':'Activities'},
            'bar':{'grouping':'Businesses'},
            'company':{'grouping':'Businesses'},
            'cafe':{'grouping':'Businesses'},
            'hotel':{'grouping':'Businesses'},
            'restaurant':{'grouping':'Businesses'},
            'cause':{'grouping':'Groups'},
            'sports_league':{'grouping':'Groups'},
            'sports_team':{'grouping':'Groups'},
            'band':{'grouping':'Organizations'},
            'government':{'grouping':'Organizations'},
            'non_profit':{'grouping':'Organizations'},
            'school':{'grouping':'Organizations'},
            'university':{'grouping':'Organizations'},
            'actor':{'grouping':'People'},
            'athlete':{'grouping':'People'},
            'author':{'grouping':'People '},
            'director':{'grouping':'People'},
            'musician':{'grouping':'People'},
            'politician':{'grouping':'People'},
            'public_figure':{'grouping':'People'},
            'city':{'grouping':'Places'},
            'country':{'grouping':'Places'},
            'landmark':{'grouping':'Places'},
            'state_province':{'grouping':'Places'},
            'album':{'grouping':'Products and Entertainment'},
            'book':{'grouping':'Products and Entertainment'},
            'drink':{'grouping':'Products and Entertainment'},
            'food':{'grouping':'Products and Entertainment'},
            'game':{'grouping':'Products and Entertainment'},
            'product':{'grouping':'Products and Entertainment'},
            'song':{'grouping':'Products and Entertainment'},
            'movie':{'grouping':'Products and Entertainment'},
            'tv_show':{'grouping':'Products and Entertainment'},
            'blog':{'grouping':'Websites '},
            'website':{'grouping':'Websites'},
            'article':{'grouping':'Websites'},
            'game.achievement':{
                'grouping': 'Game',
                'properties' : {
                    'game:points': { 'description': 'POINTS_FOR_ACHIEVEMENT'},
                },
            },
        },
        'valid_types-2' : {
            'website': {
                'namespace' : 'http://ogp.me/ns/website#',
                'properties':{}
            },
            'article': {
                'namespace' : 'http://ogp.me/ns/article#',
                'properties':{
                    'article:published_time' : {
                        'type':'datetime',
                        'description':'When the article was first published.'
                    },
                    'article:modified_time' : {
                        'type':'datetime',
                        'description':'When the article was last changed.'
                    },
                    'article:expiration_time' : {
                        'type':'datetime',
                        'description':'When the article is out of date after.'
                    },
                    'article:author' : {
                        'type':'profile',
                        'description':'Writers of the article.',
                        'array_allowed': True
                    },
                    'article:section': {
                        'type':'string',
                        'description':'A high-level section name. E.g. Technology'
                        },
                    'article:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this article.',
                        'array_allowed': True
                    },
                }
            },
            'book': {
                'namespace' : 'http://ogp.me/ns/book#',
                'properties':{
                    'book:author' : {
                        'type':'profile',
                        'description':'Who wrote this book.',
                        'array_allowed': True
                    },
                    'book:isbn' : {
                        'type':'string',
                        'description':'The ISBN'
                    },
                    'book:release_date' : {
                        'type':'datetime',
                        'description':'The date the book was released.'
                    },
                    'book:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this book.',
                        'array_allowed': True
                    },
                }
            },
            'profile': {
                'namespace' : 'http://ogp.me/ns/profile#',
                'properties':{
                    'profile:first_name' : {
                        'type':'string',
                        'description':'first name'
                    },
                    'profile:last_name' : {
                        'type':'string',
                        'description':'last name'
                    },
                    'profile:username' : {
                        'type':'string',
                        'description':'A short unique string to identify them.'
                    },
                    'profile:gender' : {
                        'type':'enum',
                        'enums':['male','female'],
                        'description':'Their gender'
                    },
                }
            },
            'video.movie': {
                'namespace' : 'http://ogp.me/ns/video#',
                'properties' : {
                    'video:actor' : {
                        'type':'profile',
                        'description':'actors in the movie',
                        'array_allowed': True
                    },
                    'video:actor:role' : {
                        'type':'string',
                        'description':'the role they played'
                    },
                    'video:director' : {
                        'type':'profile',
                        'description':'directors of the movie',
                        'array_allowed': True
                    },
                    'video:writer' : {
                        'type':'profile',
                        'description':'writers of the movie',
                        'array_allowed': True
                    },
                    'video:duration' : {
                        'type':'integer',
                        'description':'The movie\'s length in seconds',
                    },
                    'video:release_date' : {
                        'type':'datetime',
                        'description':'The date the movie was released',
                    },
                    'video:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this video.',
                        'array_allowed': True
                    },
                },
            },
            'video.episode': {
                'namespace' : 'http://ogp.me/ns/video#',
                'properties' : {
                    'video:actor' : {
                        'type':'profile',
                        'description':'actors in the movie',
                        'array_allowed': True
                    },
                    'video:actor:role' : {
                        'type':'string',
                        'description':'the role they played'
                    },
                    'video:director' : {
                        'type':'profile',
                        'description':'directors of the movie',
                        'array_allowed': True
                    },
                    'video:writer' : {
                        'type':'profile',
                        'description':'writers of the movie',
                        'array_allowed': True
                    },
                    'video:duration' : {
                        'type':'integer',
                        'description':'The movie\'s length in seconds',
                    },
                    'video:release_date' : {
                        'type':'datetime',
                        'description':'The date the movie was released',
                    },
                    'video:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this video.',
                        'array_allowed': True
                    },
                    'video:series' : {
                        'type': 'video.tv_show',
                        'description': 'Which series this episode belongs to.'
                    },
                },
            },
            'video.tv_show': {
                'namespace' : 'http://ogp.me/ns/video#',
                'properties' : {
                    'video:actor' : {
                        'type':'profile',
                        'description':'actors in the movie',
                        'array_allowed': True
                    },
                    'video:actor:role' : {
                        'type':'string',
                        'description':'the role they played'
                    },
                    'video:director' : {
                        'type':'profile',
                        'description':'directors of the movie',
                        'array_allowed': True
                    },
                    'video:writer' : {
                        'type':'profile',
                        'description':'writers of the movie',
                        'array_allowed': True
                    },
                    'video:duration' : {
                        'type':'integer',
                        'description':'The movie\'s length in seconds',
                    },
                    'video:release_date' : {
                        'type':'datetime',
                        'description':'The date the movie was released',
                    },
                    'video:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this video.',
                        'array_allowed': True
                    },
                },
            },
            'video.other': {
                'namespace' : 'http://ogp.me/ns/video#',
                'properties' : {
                    'video:actor' : {
                        'type':'profile',
                        'description':'actors in the movie',
                        'array_allowed': True
                    },
                    'video:actor:role' : {
                        'type':'string',
                        'description':'the role they played'
                    },
                    'video:director' : {
                        'type':'profile',
                        'description':'directors of the movie',
                        'array_allowed': True
                    },
                    'video:writer' : {
                        'type':'profile',
                        'description':'writers of the movie',
                        'array_allowed': True
                    },
                    'video:duration' : {
                        'type':'integer',
                        'description':'The movie\'s length in seconds',
                    },
                    'video:release_date' : {
                        'type':'datetime',
                        'description':'The date the movie was released',
                    },
                    'video:tag' : {
                        'type':'string',
                        'description':'Tag words associated with this video.',
                        'array_allowed': True
                    },
                },
            },
           'music.song': {
                'namespace' : 'http://ogp.me/ns/music#',
                'properties' : {
                    'music:duration':{
                        'type':'integer',
                        'description':'The song\'s length in seconds'
                    },
                    'music:album':{
                        'type':'music.album',
                        'description':'The album this song is from.',
                        'array_allowed':True
                    },
                    'music:album:disc':{
                        'type':'integer',
                        'description':'Which disc of the album this song is on'
                    },
                    'music:album:track':{
                        'type':'integer',
                        'description':'Which track this song is'
                    },
                    'music:musician':{
                        'type':'profile',
                        'description':'The musician that made this song',
                        'array_allowed':True
                    },
                }
            },
            'music.album': {
                'namespace' : 'http://ogp.me/ns/music#',
                'properties' : {
                    'music:song':{
                        'type':'music.song',
                        'description':'The song on this album.',
                    },
                    'music:song:disc':{
                        'type':'integer',
                        'description':'the disc the song is on for the album'
                    },
                    'music:song:track':{
                        'type':'integer',
                        'description':'the track number the song is on for the album'
                    },
                    'music:musician':{
                        'type':'profile',
                        'description':'The musician that made this song'
                    },
                    'music:release_date':{
                        'type':'datetime',
                        'description':'The date the album was released.'
                    },
                }
            },
            'music.playlist': {
                'namespace' : 'http://ogp.me/ns/music#',
                'properties' : {
                    'music:song':{
                        'type':'music.song',
                        'description':'The song',
                    },
                    'music:song:disc':{
                        'type':'integer',
                        'description':'the disc the song is on for the album'
                    },
                    'music:song:track':{
                        'type':'integer',
                        'description':'the track number the song is on for the album'
                    },
                    'music:creator':{
                        'type':'profile',
                        'description':'The creator of this playlist.'
                    }
                },
            },
            'music.radio_station': {
                'namespace' : 'http://ogp.me/ns/music#',
                'properties' : {
                    'music:creator':{
                        'type':'profile',
                        'description':'The creator of this station.'
                    },
                },
            },

        }
    },
    'og:image' : {
        'required':True,
        'type':'url',
        'description':'An image URL which should represent your object within the graph. The image must be at least 50px by 50px and have a maximum aspect ratio of 3:1. We support PNG, JPEG and GIF formats. You may include multiple og:image tags to associate multiple images with your page.',
        'properties': {
            'og:image:url' : {
                'description': 'Identical to og:image.' ,
                'type':'url',
            },
            'og:image:secure_url' : {
                'description': ' An alternate url to use if the webpage requires HTTPS.' ,
                'type':'url',
            },
            'og:image:type' : {
                'description': 'A MIME type for this image.',
                'type':'string',
            },
            'og:image:width' : {
                'description': 'The number of pixels wide.',
                'type':'integer',
            },
            'og:image:height' : {
                'description': 'The number of pixels high.',
                'type':'integer',
            },
        }
    },
    'og:url' : {
        'required':True,
        'description':'The canonical URL of your object that will be used as its permanent ID in the graph, e.g., http://www.imdb.com/title/tt0117500/',
        'type':'url',       
    },
    'og:site_name': {
        'required':False,
        'description':'A human-readable name for your site, e.g., "IMDb".',
        'type':'string',        
    },
    'og:description': {
        'required':False,
        'description':'A one to two sentence description of your page.',
        'type':'string',        
    },
    'og:isbn': {
        'required':False,
        'description':'For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.',
        'type':'string',
        },
    'og:upc': {
        'required':False,
        'description':'For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.',
        'type':'string',
    },
    'og:audio': {
        'required':False,
        'description':'A URL to an audio file to accompany this object.' ,
        'type':'url',
        'properties': {
            'og:audio:secure_url' : {
                'description': ' An alternate url to use if the webpage requires HTTPS.',
                'type':'url',
            },
            'og:audio:type' : {
                'description': 'A MIME type for this audio.',
                'type':'string',
            },
            'og:audio:title': {
                'description':'NOT IN 2.0 SPEC -- song title',
                'type':'string',
            },
            'og:audio:artist': {
                'description':'NOT IN 2.0 SPEC -- song artist',
                'type':'string',
            },
            'og:audio:album': {
                'description':'NOT IN 2.0 SPEC -- song album',
                'type':'string',
            },
        }
    },
    'og:determiner': {
        'required':False, 
        'description': """The word that appears before this object's title in a sentence. An enum of (a, an, the, "", auto). If auto is chosen, the consumer of your data should chose between "a" or "an". Default is "" (blank).""",
        'type':'enum',
        'enums': ('a', 'an', 'the', '', 'auto'),
    },
    'og:locale': {
        'required':False, 
        'description': """The locale these tags are marked up in. Of the format language_TERRITORY. Default is en_US.""",
        'type':'string',
    },
    'og:locale:alternate': {
        'required':False, 
        'description': """An array of other locales this page is available in..""",
        'type':'string',
        'array_allowed':True,
    },
    'og:video': {
        'required': False,
        'description':'A URL to a video file that complements this object. set content to url of video file. You may specify more than one og:video. If you specify more than one og:video, then og:video:type is required for each video. You must include a valid og:image for your video to be displayed in the news feed.',
        'properties': {
            'og:video:secure_url' : { 
                'description': ' An alternate url to use if the webpage requires HTTPS.' ,
                'type':'url',
            },
            'og:video:type' : { 
                'description': 'A MIME type for this video.' ,
                'type':'string',
            },
            'og:video:width' : { 
                'description': 'The number of pixels wide.' ,
                'type':'integer',
            },
            'og:video:height' : { 
                'description': 'The number of pixels high.' ,
                'type':'integer',
            },
        }
    },
}
facebook_extensions = {
    'fb:admins': { 'required':False,'description':'To associate the page with your Facebook account, add the additional property fb:admins to your page with a comma-separated list of the user IDs or usernames of the Facebook accounts who own the page, e.g.: <meta property="fb:admins" content="USER_ID1,USER_ID2"/>'},
    'fb:app_id': {'required':False,'description':'A Facebook Platform application ID that administers this page.'},
}



def validate_item(info_dict,value):
    if info_dict['type'] == 'string':
        if isinstance( value, types.StringTypes ):
            return True
        return False
    if info_dict['type'] == 'boolean':
        try:
            success= (0,1,'true','false').index(value)
            return True
        except ValueError:
            return False
    elif info_dict['type'] == 'enum':
        try:
            success= info_dict.enums.index(value)
            return True
        except ValueError:
            return False
    elif info_dict['type'] == 'integer':
        try:
            if isinstance( value, types.IntegerType ):
                return True
            else:
               # coercing an int(value) into a string should catch utf8&string types, and fail on floats
               # this can raise a valueerror though
               if value == "%s" % int(value):
                   return True
        except ValueError:
            return False
    elif info_dict['type'] == 'datetime':
        if isinstance( value, datetime.date ) or isinstance( value, datetime.datetime ) :
            return True
        if isinstance( value, types.StringTypes ) :
            for test in regex_dates :
                if re.match( regex_dates[test], value ):
                    return True
            return False
    elif info_dict['type'] == 'url':
        if re.match( regex_url, value ):
            return True
        return False

    elif info_dict['type'] == 'profile':
    	## TO DO
    	## this involves looking for other fields.
    	return True

    return False




class OpenGraphItem(object):
    _data= None
    _errors= None
    def __init__(self,sets=None):
        self._data= {}
        self._errors= {}
        if sets:
           self.set_many(sets)

    def set_many( self, pairs ):
        for pair in pairs :
            ( f,v ) = pair
            self.set(f,v)


    def set(self,field,value,append=False):
        if not append:
            self._data[field]= value
        else:
            if field not in self._data:
               self._data[field]= []
            else:
                if type(self._data[field]) is not types.ListType:
                   self._data[field]= [self._data[field],]
            self._data[field].append( value )

    def validate(self,facebook=False,schema1=False,schema2=True):
        errors= { 'critical':{} , 'recommended': {}}
        def _errror(level,item,message):
            #if level not in errors:
            #    errors[level]= {}
            errors[level][item]= message

        for i in og_properties:
            # make sure that everything in og_properties which is required is present
            if og_properties[i]['required'] and ( i not in self._data ):
                _errror('critical',i,"Missing Required Element")
            elif og_properties[i]['required'] and ( i in self._data ):
                if not validate_item( og_properties[i] , self._data[i]):
                    _errror('critical',i,"Required Element does not validate")
            else: 
                if i in self._data:
                    if not validate_item( og_properties[i] , self._data[i]):
                        _errror('recommended',i,"non-required Element does not validate")


        if 'og:type' not in errors:
            _error= None
            if schema1 :
                if self._data['og:type'] not in og_properties['og:type']['valid_types-1'] :
                   _errror('critical','og:type',"Invalid og:type")
            elif schema2:
                if self._data['og:type'] not in og_properties['og:type']['valid_types-2'] :
                   _errror('critical','og:type',"Invalid og:type")
                for subtype in og_properties['og:type']['valid_types-2'][self._data['og:type']]['properties']:
                    info= og_properties['og:type']['valid_types-2'][self._data['og:type']]
                    info_dict= info['properties'][subtype]
                    error= None
                    value= None
                    if subtype in self._data:
                        value= self._data[subtype]
                    if 'required' in info and info['required']:
                        if subtype not in og_properties :
                            _errror('critical','%s'%subtype,"Missing required subtype")
                        elif not validate_item(info_dict,value) :
                            _errror('critical','%s'%subtype,"Required subtype does not validate correctly")
                    else:
                        if ( subtype not in self._data ) :
                            _errror('recommended','%s'%subtype,"non-required subtype not included")
                        else:
                            if not validate_item(info_dict,value) :
                               _errror('recommended','%s'%subtype,"non-required subtype does not validate correctly")


        self._errors= errors
        if errors['critical']:
            return False
        return True

    def errors(self):
        return self._errors

    def as_html(self,debug=False):
        output= []
        for i in self._data :
            if type(i) == types.ListType :
                pass
            else:
                _error= ''
                if debug:
                    if i in self._errors['critical']:
                        _error= ' critical-error="%s"' % self._errors['critical'][i].encode('utf8')
                    elif i in self._errors['recommended']:
                        _error= ' recommended-error="%s"' % self._errors['recommended'][i].encode('utf8')
                output.append( """<meta property="%s" content="%s"%s/>""" % ( i , urllib2.quote(self._data[i].encode('utf8')) , _error ) )
        output= '\n'.join(output)
        return output



def pyramid_opengraph_item(request):
    """gets the opengraph item attached to the pyramid request object. if non exists, makes a new one , attaches and returns it."""
    if not hasattr( request , 'pyramid_opengraph_item' ) :
        request.pyramid_opengraph_item= OpenGraphItem()
    return request.pyramid_opengraph_item


def pylons_opengraph_item(c):
    """gets the opengraph item attached to the pylons c object. if non exists, makes a new one , attaches and returns it."""
    if not hasattr( c , 'pyramid_opengraph_item' ) :
        c.pyramid_opengraph_item= OpenGraphItem()
    return c.pyramid_opengraph_item




if __name__ == '__main__':
    a= OpenGraphItem()
    a.set('og:title','MyWebsite')
    a.set('og:type','article')
    a.set_many( (('og:url','http://f.me'),('og:image','http://f.me/a.png'),('article:author','abc'),('article:published_time','2012-01-10')) )
    status = a.validate()
    if status:
       print "object ok"
    else:
       print "object not ok"
    print a.as_html(debug=True)
       