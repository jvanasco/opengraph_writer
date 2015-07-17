from . import OpenGraphItem


def includeme(config):
    """the pyramid includeme command
    including this will automatically setup the OpenGraphItem object for every request
    """
    config.add_request_method(
        'opengraph_writer.pyramid_helpers.new_OpenGraphItem',
        'opengraph_item',
        reify=True,
    )


def new_OpenGraphItem(request):
    """simply creates a new hub"""
    return OpenGraphItem()
