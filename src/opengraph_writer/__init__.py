from __future__ import print_function

"""
==============

The followig information about Open Graph 1.0 is copied verbatim from Facebook, and remains their copyright:

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

The following is taken from the 2.0 spec -- http://ogp.me/, and remains their copyright

Arrays
    If a tag can have multiple values, just put multiple versions of the same <meta> tag on your page. The first tag (from top to bottom) is given preference during conflicts.

        <meta property="og:image" content="http://example.com/rock.jpg" />
        <meta property="og:image" content="http://example.com/rock2.jpg" />

    Put structured properties after you declare their root tag. Whenever another root element is parsed, that structured property is considered to be done and another one is started.
"""

__VERSION__ = "0.4.0"

# stdlib
import datetime
import re
import typing

# pypi
from metadata_utils import html_attribute_escape

# typing
_OG_KV = typing.Tuple[str, str]
_OG_KV_MANY = typing.List[_OG_KV]
_OG_SET = typing.Tuple[str, typing.Any]
_OG_DATA = typing.Dict[str, typing.Any]


# http://en.wikipedia.org/wiki/ISO_8601
regex_dates = {
    #  Date    2012-02-02
    "date": re.compile("^([0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])$"),
    # Ordinal date:    2012-033
    "ordinal_date": re.compile(
        "^([0-9]{4})-(36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9])$"
    ),
    # Date with week number:   2012-W05-4
    "week_number": re.compile("^([0-9]{4})-?W(5[0-3]|[1-4][0-9]|0[1-9])-?([1-7])$"),
    # Separate date and time in UTC:   2012-02-02 15:29Z
    "datetime, UTC": re.compile(
        "^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$"
    ),
}


# basically just testing that the string starts with http/https, and has some resemeblence of a domain on it.  after an optional trailing slash, i don't need to make this super accurate
regex_url = re.compile(r"""^http[s]?:\/\/[a-z0-9.\-]+[.][a-z]{2,4}\/?""")


OG_PROPERTIES: typing.Dict[str, dict] = {
    "og:title": {
        "required": True,
        "description": 'The title of your object as it should appear within the graph, e.g., "The Rock".',
        "type": "string",
    },
    "og:type": {
        "required": True,
        "description": 'The type of your object, e.g., "movie". See the complete list of supported types.',
        "type": "string",
        "valid_types-1": {
            "activity": {"grouping": "Activities"},
            "sport": {"grouping": "Activities"},
            "bar": {"grouping": "Businesses"},
            "company": {"grouping": "Businesses"},
            "cafe": {"grouping": "Businesses"},
            "hotel": {"grouping": "Businesses"},
            "restaurant": {"grouping": "Businesses"},
            "cause": {"grouping": "Groups"},
            "sports_league": {"grouping": "Groups"},
            "sports_team": {"grouping": "Groups"},
            "band": {"grouping": "Organizations"},
            "government": {"grouping": "Organizations"},
            "non_profit": {"grouping": "Organizations"},
            "school": {"grouping": "Organizations"},
            "university": {"grouping": "Organizations"},
            "actor": {"grouping": "People"},
            "athlete": {"grouping": "People"},
            "author": {"grouping": "People "},
            "director": {"grouping": "People"},
            "musician": {"grouping": "People"},
            "politician": {"grouping": "People"},
            "public_figure": {"grouping": "People"},
            "city": {"grouping": "Places"},
            "country": {"grouping": "Places"},
            "landmark": {"grouping": "Places"},
            "state_province": {"grouping": "Places"},
            "album": {"grouping": "Products and Entertainment"},
            "book": {"grouping": "Products and Entertainment"},
            "drink": {"grouping": "Products and Entertainment"},
            "food": {"grouping": "Products and Entertainment"},
            "game": {"grouping": "Products and Entertainment"},
            "product": {"grouping": "Products and Entertainment"},
            "song": {"grouping": "Products and Entertainment"},
            "movie": {"grouping": "Products and Entertainment"},
            "tv_show": {"grouping": "Products and Entertainment"},
            "blog": {"grouping": "Websites "},
            "website": {"grouping": "Websites"},
            "article": {"grouping": "Websites"},
            "game.achievement": {
                "grouping": "Game",
                "properties": {
                    "game:points": {"description": "POINTS_FOR_ACHIEVEMENT"}
                },
            },
        },
        "valid_types-2": {
            "website": {"namespace": "http://ogp.me/ns/website#", "properties": {}},
            "article": {
                "namespace": "http://ogp.me/ns/article#",
                "properties": {
                    "article:published_time": {
                        "type": "datetime",
                        "description": "When the article was first published.",
                    },
                    "article:modified_time": {
                        "type": "datetime",
                        "description": "When the article was last changed.",
                    },
                    "article:expiration_time": {
                        "type": "datetime",
                        "description": "When the article is out of date after.",
                    },
                    "article:author": {
                        "type": "profile",
                        "description": "Writers of the article.",
                        "array_allowed": True,
                    },
                    "article:section": {
                        "type": "string",
                        "description": "A high-level section name. E.g. Technology",
                    },
                    "article:tag": {
                        "type": "string",
                        "description": "Tag words associated with this article.",
                        "array_allowed": True,
                    },
                },
            },
            "book": {
                "namespace": "http://ogp.me/ns/book#",
                "properties": {
                    "book:author": {
                        "type": "profile",
                        "description": "Who wrote this book.",
                        "array_allowed": True,
                    },
                    "book:isbn": {"type": "string", "description": "The ISBN"},
                    "book:release_date": {
                        "type": "datetime",
                        "description": "The date the book was released.",
                    },
                    "book:tag": {
                        "type": "string",
                        "description": "Tag words associated with this book.",
                        "array_allowed": True,
                    },
                },
            },
            "profile": {
                "namespace": "http://ogp.me/ns/profile#",
                "properties": {
                    "profile:first_name": {
                        "type": "string",
                        "description": "first name",
                    },
                    "profile:last_name": {"type": "string", "description": "last name"},
                    "profile:username": {
                        "type": "string",
                        "description": "A short unique string to identify them.",
                    },
                    "profile:gender": {
                        "type": "enum",
                        "enums": ["male", "female"],
                        "description": "Their gender",
                    },
                },
            },
            "video.movie": {
                "namespace": "http://ogp.me/ns/video#",
                "properties": {
                    "video:actor": {
                        "type": "profile",
                        "description": "actors in the movie",
                        "array_allowed": True,
                    },
                    "video:actor:role": {
                        "type": "string",
                        "description": "the role they played",
                    },
                    "video:director": {
                        "type": "profile",
                        "description": "directors of the movie",
                        "array_allowed": True,
                    },
                    "video:writer": {
                        "type": "profile",
                        "description": "writers of the movie",
                        "array_allowed": True,
                    },
                    "video:duration": {
                        "type": "integer",
                        "description": "The movie's length in seconds",
                    },
                    "video:release_date": {
                        "type": "datetime",
                        "description": "The date the movie was released",
                    },
                    "video:tag": {
                        "type": "string",
                        "description": "Tag words associated with this video.",
                        "array_allowed": True,
                    },
                },
            },
            "video.episode": {
                "namespace": "http://ogp.me/ns/video#",
                "properties": {
                    "video:actor": {
                        "type": "profile",
                        "description": "actors in the movie",
                        "array_allowed": True,
                    },
                    "video:actor:role": {
                        "type": "string",
                        "description": "the role they played",
                    },
                    "video:director": {
                        "type": "profile",
                        "description": "directors of the movie",
                        "array_allowed": True,
                    },
                    "video:writer": {
                        "type": "profile",
                        "description": "writers of the movie",
                        "array_allowed": True,
                    },
                    "video:duration": {
                        "type": "integer",
                        "description": "The movie's length in seconds",
                    },
                    "video:release_date": {
                        "type": "datetime",
                        "description": "The date the movie was released",
                    },
                    "video:tag": {
                        "type": "string",
                        "description": "Tag words associated with this video.",
                        "array_allowed": True,
                    },
                    "video:series": {
                        "type": "video.tv_show",
                        "description": "Which series this episode belongs to.",
                    },
                },
            },
            "video.tv_show": {
                "namespace": "http://ogp.me/ns/video#",
                "properties": {
                    "video:actor": {
                        "type": "profile",
                        "description": "actors in the movie",
                        "array_allowed": True,
                    },
                    "video:actor:role": {
                        "type": "string",
                        "description": "the role they played",
                    },
                    "video:director": {
                        "type": "profile",
                        "description": "directors of the movie",
                        "array_allowed": True,
                    },
                    "video:writer": {
                        "type": "profile",
                        "description": "writers of the movie",
                        "array_allowed": True,
                    },
                    "video:duration": {
                        "type": "integer",
                        "description": "The movie's length in seconds",
                    },
                    "video:release_date": {
                        "type": "datetime",
                        "description": "The date the movie was released",
                    },
                    "video:tag": {
                        "type": "string",
                        "description": "Tag words associated with this video.",
                        "array_allowed": True,
                    },
                },
            },
            "video.other": {
                "namespace": "http://ogp.me/ns/video#",
                "properties": {
                    "video:actor": {
                        "type": "profile",
                        "description": "actors in the movie",
                        "array_allowed": True,
                    },
                    "video:actor:role": {
                        "type": "string",
                        "description": "the role they played",
                    },
                    "video:director": {
                        "type": "profile",
                        "description": "directors of the movie",
                        "array_allowed": True,
                    },
                    "video:writer": {
                        "type": "profile",
                        "description": "writers of the movie",
                        "array_allowed": True,
                    },
                    "video:duration": {
                        "type": "integer",
                        "description": "The movie's length in seconds",
                    },
                    "video:release_date": {
                        "type": "datetime",
                        "description": "The date the movie was released",
                    },
                    "video:tag": {
                        "type": "string",
                        "description": "Tag words associated with this video.",
                        "array_allowed": True,
                    },
                },
            },
            "music.song": {
                "namespace": "http://ogp.me/ns/music#",
                "properties": {
                    "music:duration": {
                        "type": "integer",
                        "description": "The song's length in seconds",
                    },
                    "music:album": {
                        "type": "music.album",
                        "description": "The album this song is from.",
                        "array_allowed": True,
                    },
                    "music:album:disc": {
                        "type": "integer",
                        "description": "Which disc of the album this song is on",
                    },
                    "music:album:track": {
                        "type": "integer",
                        "description": "Which track this song is",
                    },
                    "music:musician": {
                        "type": "profile",
                        "description": "The musician that made this song",
                        "array_allowed": True,
                    },
                },
            },
            "music.album": {
                "namespace": "http://ogp.me/ns/music#",
                "properties": {
                    "music:song": {
                        "type": "music.song",
                        "description": "The song on this album.",
                    },
                    "music:song:disc": {
                        "type": "integer",
                        "description": "the disc the song is on for the album",
                    },
                    "music:song:track": {
                        "type": "integer",
                        "description": "the track number the song is on for the album",
                    },
                    "music:musician": {
                        "type": "profile",
                        "description": "The musician that made this song",
                    },
                    "music:release_date": {
                        "type": "datetime",
                        "description": "The date the album was released.",
                    },
                },
            },
            "music.playlist": {
                "namespace": "http://ogp.me/ns/music#",
                "properties": {
                    "music:song": {"type": "music.song", "description": "The song"},
                    "music:song:disc": {
                        "type": "integer",
                        "description": "the disc the song is on for the album",
                    },
                    "music:song:track": {
                        "type": "integer",
                        "description": "the track number the song is on for the album",
                    },
                    "music:creator": {
                        "type": "profile",
                        "description": "The creator of this playlist.",
                    },
                },
            },
            "music.radio_station": {
                "namespace": "http://ogp.me/ns/music#",
                "properties": {
                    "music:creator": {
                        "type": "profile",
                        "description": "The creator of this station.",
                    }
                },
            },
        },
    },
    "og:image": {
        "required": True,
        "type": "url",
        "description": "An image URL which should represent your object within the graph. The image must be at least 50px by 50px and have a maximum aspect ratio of 3:1. We support PNG, JPEG and GIF formats. You may include multiple og:image tags to associate multiple images with your page.",
        "properties": {
            "og:image:url": {"description": "Identical to og:image.", "type": "url"},
            "og:image:secure_url": {
                "description": " An alternate url to use if the webpage requires HTTPS.",
                "type": "url",
            },
            "og:image:type": {
                "description": "A MIME type for this image.",
                "type": "string",
            },
            "og:image:width": {
                "description": "The number of pixels wide.",
                "type": "integer",
            },
            "og:image:height": {
                "description": "The number of pixels high.",
                "type": "integer",
            },
        },
    },
    "og:url": {
        "required": True,
        "description": "The canonical URL of your object that will be used as its permanent ID in the graph, e.g., http://www.imdb.com/title/tt0117500/",
        "type": "url",
    },
    "og:site_name": {
        "required": False,
        "description": 'A human-readable name for your site, e.g., "IMDb".',
        "type": "string",
    },
    "og:description": {
        "required": False,
        "description": "A one to two sentence description of your page.",
        "type": "string",
    },
    "og:isbn": {
        "required": False,
        "description": "For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.",
        "type": "string",
    },
    "og:upc": {
        "required": False,
        "description": "For products which have a UPC code or ISBN number, you can specify them using the og:upc and og:isbn properties. These properties help uniquely identify products.",
        "type": "string",
    },
    "og:audio": {
        "required": False,
        "description": "A URL to an audio file to accompany this object.",
        "type": "url",
        "properties": {
            "og:audio:secure_url": {
                "description": " An alternate url to use if the webpage requires HTTPS.",
                "type": "url",
            },
            "og:audio:type": {
                "description": "A MIME type for this audio.",
                "type": "string",
            },
            "og:audio:title": {
                "description": "NOT IN 2.0 SPEC -- song title",
                "type": "string",
            },
            "og:audio:artist": {
                "description": "NOT IN 2.0 SPEC -- song artist",
                "type": "string",
            },
            "og:audio:album": {
                "description": "NOT IN 2.0 SPEC -- song album",
                "type": "string",
            },
        },
    },
    "og:determiner": {
        "required": False,
        "description": """The word that appears before this object's title in a sentence. An enum of (a, an, the, "", auto). If auto is chosen, the consumer of your data should chose between "a" or "an". Default is "" (blank).""",
        "type": "enum",
        "enums": ("a", "an", "the", "", "auto"),
    },
    "og:locale": {
        "required": False,
        "description": """The locale these tags are marked up in. Of the format language_TERRITORY. Default is en_US.""",
        "type": "string",
    },
    "og:locale:alternate": {
        "required": False,
        "description": """An array of other locales this page is available in..""",
        "type": "string",
        "array_allowed": True,
    },
    "og:video": {
        "required": False,
        "description": "A URL to a video file that complements this object. set content to url of video file. You may specify more than one og:video. If you specify more than one og:video, then og:video:type is required for each video. You must include a valid og:image for your video to be displayed in the news feed.",
        "properties": {
            "og:video:secure_url": {
                "description": " An alternate url to use if the webpage requires HTTPS.",
                "type": "url",
            },
            "og:video:type": {
                "description": "A MIME type for this video.",
                "type": "string",
            },
            "og:video:width": {
                "description": "The number of pixels wide.",
                "type": "integer",
            },
            "og:video:height": {
                "description": "The number of pixels high.",
                "type": "integer",
            },
        },
    },
}
facebook_extensions = {
    "fb:admins": {
        "required": False,
        "description": 'To associate the page with your Facebook account, add the additional property fb:admins to your page with a comma-separated list of the user IDs or usernames of the Facebook accounts who own the page, e.g.: <meta property="fb:admins" content="USER_ID1,USER_ID2"/>',
    },
    "fb:app_id": {
        "required": False,
        "description": "A Facebook Platform application ID that administers this page.",
    },
}

# deprecated
og_properties = OG_PROPERTIES


class OGErrors(dict):
    def __init__(self):
        self["critical"] = {}
        self["recommended"] = {}
        self["not_validated"] = []


def validate_item(
    info_dict: typing.Dict[str, typing.Any],
    value: typing.Any,
) -> bool:
    if info_dict["type"] == "string":
        if isinstance(value, str):
            return True
        return False

    elif info_dict["type"] == "boolean":
        try:
            _success = (0, 1, "true", "false").index(value)  # noqa: F841
            return True
        except ValueError:
            return False

    elif info_dict["type"] == "enum":
        try:
            _success = info_dict["enums"].index(value)  # noqa: F841
            return True
        except ValueError:
            return False

    elif info_dict["type"] == "integer":
        try:
            if isinstance(value, int):
                return True
            else:
                # coercing an int(value) into a string should catch utf8&string types, and fail on floats
                # this can raise a valueerror though
                if value == "%s" % int(value):
                    return True
        except ValueError:
            return False

    elif info_dict["type"] == "datetime":
        if isinstance(value, (datetime.date, datetime.datetime)):
            return True
        if isinstance(value, str):
            for test in regex_dates:
                if re.match(regex_dates[test], value):
                    return True
            return False

    elif info_dict["type"] == "url":
        if re.match(regex_url, value):
            return True
        return False

    elif info_dict["type"] == "profile":
        # TODO
        # this involves looking for other fields.
        return True

    return False


def stringify(value: typing.Any) -> str:
    """turns a value into a string if needed"""
    if isinstance(value, bool):
        if value:
            return "true"
        return "false"
    elif isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, datetime.date):
        return value.isoformat()
    return value


class OpenGraphItem(object):
    _data: _OG_DATA = {}
    _errors: typing.Optional[OGErrors] = None

    def __init__(
        self,
        sets: typing.Optional[_OG_KV_MANY] = None,
    ) -> None:
        self._data = {}
        if sets:
            self.set_many(sets)

    def set_many(
        self,
        pairs: _OG_KV_MANY,
    ) -> None:
        for pair in pairs:
            (f, v) = pair
            self.set(f, v)

    def set(
        self,
        field: str,
        value: str,
        append: bool = False,
    ) -> None:
        if not append:
            self._data[field] = value
        else:
            if field not in self._data:
                self._data[field] = []
            else:
                if not isinstance(self._data[field], list):
                    self._data[field] = [self._data[field]]
            self._data[field].append(value)

    def validate(
        self,
        facebook: bool = False,
        schema1: bool = False,
        schema2: bool = True,
    ) -> bool:
        """
        Validate the object

        :param facebook: validate against the facebook extensions?
        :type resp: bool
        :param schema1: validate against schema1? Default: `False`.
            This is likely the schema before opengraph was open sourced.
            It is very basic, and only checks for a supported "og:type"
        :type resp: bool
        :param schema2: validate against schema2? Default: `True`
            This appears to be the current opengraph protocol.
            This will process both the og:type and the subtypes.
        :type resp: bool

        :rtype: bool
        """
        if facebook is True:
            raise ValueError("Support for Facebook Extensions is not built yet")
        if schema1 and schema2:
            raise ValueError("Validate against either schema1 or schema2")

        errors = OGErrors()

        def _set_error(
            level: str,
            item: str,
            message: str,
        ) -> None:
            # if level not in errors:
            #    errors[level]= {}
            errors[level][item] = message

        validate_fields = set(self._data.keys())

        # make sure that everything in OG_PROPERTIES:
        # 1) is present if required
        # 2) is valid if not required
        # 3) is valid if not required
        for i in OG_PROPERTIES:
            if OG_PROPERTIES[i]["required"]:
                if i not in self._data:
                    _set_error("critical", i, "Missing Required Element")
                else:
                    # required; check validity
                    validate_fields.remove(i)
                    if not validate_item(OG_PROPERTIES[i], self._data[i]):
                        _set_error("critical", i, "Required Element does not validate")
            else:
                # not required; check validity
                if i in self._data:
                    validate_fields.remove(i)
                    if not validate_item(OG_PROPERTIES[i], self._data[i]):
                        _set_error(
                            "recommended", i, "non-required Element does not validate"
                        )

        og_type = self._data.get("og:type")

        if schema1:
            # schema1 only checks for validity of the valid type
            if not og_type:
                _set_error("critical", "og:type", "Missing og:type")
            else:
                if og_type not in OG_PROPERTIES["og:type"]["valid_types-1"]:
                    _set_error("critical", "og:type", "Invalid og:type")

        if schema2:
            if not og_type:
                _set_error("critical", "og:type", "Missing og:type")
            else:
                if og_type not in OG_PROPERTIES["og:type"]["valid_types-2"]:
                    _set_error("critical", "og:type", "Invalid og:type")
                else:
                    # validate all the likely subtypes
                    og_type_dict = OG_PROPERTIES["og:type"]["valid_types-2"][og_type]
                    for subtype in OG_PROPERTIES["og:type"]["valid_types-2"][og_type][
                        "properties"
                    ]:
                        subtype_dict = og_type_dict["properties"][subtype]
                        value = None
                        if subtype in self._data:
                            value = self._data[subtype]
                        if "required" in og_type_dict and og_type_dict["required"]:
                            if subtype not in OG_PROPERTIES:
                                _set_error(
                                    "critical",
                                    "%s" % subtype,
                                    "Missing required subtype",
                                )
                            else:
                                validate_fields.remove(subtype)
                                if not validate_item(subtype_dict, value):
                                    _set_error(
                                        "critical",
                                        "%s" % subtype,
                                        "Required subtype does not validate correctly",
                                    )
                        else:
                            if subtype not in self._data:
                                _set_error(
                                    "recommended",
                                    "%s" % subtype,
                                    "non-required subtype not included",
                                )
                            else:
                                validate_fields.remove(subtype)
                                if not validate_item(subtype_dict, value):
                                    _set_error(
                                        "recommended",
                                        "%s" % subtype,
                                        "non-required subtype does not validate correctly",
                                    )

        if validate_fields:
            errors["not_validated"] = list(validate_fields)
        self._errors = errors
        if errors["critical"]:
            return False
        return True

    def errors(self) -> OGErrors:
        if self._errors is None:
            raise ValueError("You must call `.validate()` first")
        return self._errors

    def as_html(
        self,
        debug: bool = False,
    ) -> str:
        _output = []
        _keys = sorted(self._data.keys())
        if self._errors is None:
            return ""
        for k in _keys:
            v = self._data[k]
            _error = ""
            if debug:
                if k in self._errors["critical"]:
                    _error = ' critical-error="%s"' % html_attribute_escape(
                        self._errors["critical"][k]
                    )
                elif k in self._errors["recommended"]:
                    _error = ' recommended-error="%s"' % html_attribute_escape(
                        self._errors["recommended"][k]
                    )
            if isinstance(v, list):
                for i in v:
                    i = stringify(i)
                    _output.append(
                        """<meta property="%s" content="%s"%s/>"""
                        % (html_attribute_escape(k), html_attribute_escape(i), _error)
                    )
            else:
                v = stringify(v)
                _output.append(
                    """<meta property="%s" content="%s"%s/>"""
                    % (html_attribute_escape(k), html_attribute_escape(v), _error)
                )
        output = "\n".join(_output)
        return output
