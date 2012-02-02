"""
v 0.0.1

Goal:
    
    i need a lightweight package that can do the following:

        1. create an object to store open graph metadata for a url
        2. store that object, and bring it back to continually populate and eventually print during page generation
        3. validate itself at least trivially, so i don't have to do dns tricks to let the facebook linter/debugger work wherever i am
        
    
    to do that :
    
        1. consolidate documentation on open graph 1.0 and 2.0
            - done
            
        2. create structured data describing the open graph protocls
            - largely done. 
            - left to do:
                -- most of the properties for the 2.0 branch
                -- integrate the validation types
        
        3. create an object that can store og data , validate itself, and print itself out
            - just started
            - can store data and print, but not proper array support

        4. create some helpers for pyramid and pylons

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

og_properties = {
    'og:title' : {'required':True, 'description': 'The title of your object as it should appear within the graph, e.g., "The Rock".'},
    'og:type' : {
        'required':True, 
        'description':'The type of your object, e.g., "movie". See the complete list of supported types.',
        'valid_types_1' : { 
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
        'valid_types_2' : {
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
        'description':'An image URL which should represent your object within the graph. The image must be at least 50px by 50px and have a maximum aspect ratio of 3:1. We support PNG, JPEG and GIF formats. You may include multiple og:image tags to associate multiple images with your page.',
        'properties': {
            'og:image:url' : { 'description': 'Identical to og:image.' },
            'og:image:secure_url' : { 'description': ' An alternate url to use if the webpage requires HTTPS.' },
            'og:image:type' : { 'description': 'A MIME type for this image.' },
            'og:image:width' : { 'description': 'The number of pixels wide.' },
            'og:image:height' : { 'description': 'The number of pixels high.' },
        }
    },
    'og:url' : {'required':True,'description':'The canonical URL of your object that will be used as its permanent ID in the graph, e.g., http://www.imdb.com/title/tt0117500/'},
    'og:site_name': {'required':False, 'description':'A human-readable name for your site, e.g., "IMDb".'},
    'og:description': {'required':False, 'description':'A one to two sentence description of your page.'},
    'og:isbn': {'required':False, 'description':'For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.'},
    'og:upc': {'required':False, 'description':'For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.'},
    'og:audio': { 
        'required':False,
        'description':'A URL to an audio file to accompany this object.' ,
        'properties': {
            'og:audio:secure_url' : { 'description': ' An alternate url to use if the webpage requires HTTPS.' },
            'og:audio:type' : { 'description': 'A MIME type for this audio.' },
            'og:audio:title': { 'description':'NOT IN 2.0 SPEC -- song title' },
            'og:audio:artist': { 'description':'NOT IN 2.0 SPEC -- song artist' },
            'og:audio:album': { 'description':'NOT IN 2.0 SPEC -- song album' },
        }
    },
    'og:determiner': {'required':False, 'description': """The word that appears before this object's title in a sentence. An enum of (a, an, the, "", auto). If auto is chosen, the consumer of your data should chose between "a" or "an". Default is "" (blank)."""},
    'og:locale': {'required':False, 'description': """The locale these tags are marked up in. Of the format language_TERRITORY. Default is en_US."""},
    'og:locale:alternate': {'required':False, 'description': """An array of other locales this page is available in.."""},
    'og:video': { 
        'required': False,
        'description':'A URL to a video file that complements this object. set content to url of video file. You may specify more than one og:video. If you specify more than one og:video, then og:video:type is required for each video. You must include a valid og:image for your video to be displayed in the news feed.',
        'properties': {
            'og:video:secure_url' : { 'description': ' An alternate url to use if the webpage requires HTTPS.' },
            'og:video:type' : { 'description': 'A MIME type for this video.' },
            'og:video:width' : { 'description': 'The number of pixels wide.' },
            'og:video:height' : { 'description': 'The number of pixels high.' },
        }
    },
}
facebook_extensions = {
    'fb:admins': { 'required':False,'description':'To associate the page with your Facebook account, add the additional property fb:admins to your page with a comma-separated list of the user IDs or usernames of the Facebook accounts who own the page, e.g.: <meta property="fb:admins" content="USER_ID1,USER_ID2"/>'},
    'fb:app_id': {'required':False,'description':'A Facebook Platform application ID that administers this page.'},
}


import types
import urllib2


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

    def validate(self,facebook=False):
        errors= {}
        for i in og_properties:
            if og_properties[i]['required'] and i not in self._data :
                errors[i]= "Missing Required Element"
        if 'og:type' not in errors:
            _error= None
            if self._data['og:type'] not in og_properties['og:type']['valid_types_1']:
                _error= True
            elif self._data['og:type'] not in og_properties['og:type']['valid_types_2']:
                _error= True
            if _error :
                errors['og:type']= "Invalid og:type"
        self._errors= errors
        if errors:
            return False
        return True
    
    def errors(self):
        return self._errors
        
    def as_html(self):
        output= []
        for i in self._data :
            if type(i) == types.ListType :
                pass
            else:
                output.append( """<meta property="%s" content="%s"/>""" % ( i , urllib2.quote(self._data[i].encode('utf8') ) ) )
        output= '\n'.join(output)
        return output



def pyramid_opengraph_item(request):
    """UNTESTED! gets the opengraph item attached to the pyramid request's tmpl_context object. if non exists, makes a new one , attaches and returns it."""
    if not hasattr( request.tmpl_context , 'pyramid_opengraph_item' ) :
        request.tmpl_context.pyramid_opengraph_item= OpenGraphItem()
    return request.tmpl_context.pyramid_opengraph_item


def pylons_opengraph_item(c):
    """UNTESTED! gets the opengraph item attached to the pylons c object. if non exists, makes a new one , attaches and returns it."""
    if not hasattr( c , 'pyramid_opengraph_item' ) :
        c.pyramid_opengraph_item= OpenGraphItem()
    return c.pyramid_opengraph_item


    

if __name__ == '__main__':
    a= OpenGraphItem()
    a.set('og:title','MyWebsite')
    status = a.validate()
    if status:
       print "object ok"
    else:
       print "object not ok"
       print a.errors()
    print a.as_html()
       